const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');
const { MCPManager } = require('./src/mcp-manager');
const { Logger } = require('./src/logger');

let lspClient = null;
let mcpManager = null;
let logger = null;
let statusBarItem = null;

function getConfig() {
    const cfg = vscode.workspace.getConfiguration('ailang.mcp');
    return {
        autoStart: cfg.get('autoStart', true),
        command: cfg.get('command', 'ail'),
        args: cfg.get('args', ['mcp']),
        timeout: cfg.get('timeout', 30000),
        maxReconnectAttempts: cfg.get('maxReconnectAttempts', 3),
    };
}

function updateStatusBar(state) {
    if (!statusBarItem) return;
    switch (state) {
        case 'running':
            statusBarItem.text = '$(robot) AILang MCP: Running';
            statusBarItem.tooltip = 'AILang MCP server is running';
            statusBarItem.backgroundColor = undefined;
            break;
        case 'starting':
        case 'reconnecting':
            statusBarItem.text = '$(sync~spin) AILang MCP: Starting...';
            statusBarItem.tooltip = 'AILang MCP server is starting';
            statusBarItem.backgroundColor = undefined;
            break;
        case 'stopped':
            statusBarItem.text = '$(circle-slash) AILang MCP: Stopped';
            statusBarItem.tooltip = 'AILang MCP server is stopped';
            statusBarItem.backgroundColor = undefined;
            break;
        case 'failed':
            statusBarItem.text = '$(error) AILang MCP: Failed';
            statusBarItem.tooltip = 'AILang MCP server failed to start';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            break;
    }
}

async function startMCP() {
    if (!mcpManager) return;
    try {
        await mcpManager.start();
    } catch (err) {
        logger.error(`MCP start failed: ${err.message}`);
    }
}

async function stopMCP() {
    if (!mcpManager) return;
    await mcpManager.stop();
}

async function restartMCP() {
    if (!mcpManager) return;
    await mcpManager.restart();
}

async function compileCurrentFile() {
    if (!mcpManager || !mcpManager.isRunning) {
        vscode.window.showWarningMessage('AILang MCP server is not running');
        return;
    }
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
    }
    const source = editor.document.getText();
    try {
        const result = await mcpManager.client.callTool('compile_source', { source });
        const content = result.content?.[0]?.text;
        if (content) {
            const parsed = JSON.parse(content);
            if (parsed.success) {
                vscode.window.showInformationMessage('AILang: Compilation successful');
            } else {
                const diags = parsed.diagnostics || [];
                const msg = diags.map(d => `${d.code}: ${d.message}`).join('\n');
                vscode.window.showErrorMessage(`AILang compilation failed:\n${msg}`);
            }
        }
    } catch (err) {
        vscode.window.showErrorMessage(`MCP compile failed: ${err.message}`);
    }
}

async function explainDiagnostic() {
    if (!mcpManager || !mcpManager.isRunning) {
        vscode.window.showWarningMessage('AILang MCP server is not running');
        return;
    }
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const diagnostics = vscode.languages.getDiagnostics(editor.document.uri);
    if (diagnostics.length === 0) {
        vscode.window.showInformationMessage('No diagnostics in current file');
        return;
    }

    const pos = editor.selection.active;
    const diag = diagnostics.find(d => d.range.contains(pos));
    if (!diag) {
        vscode.window.showInformationMessage('No diagnostic under cursor');
        return;
    }

    const code = typeof diag.code === 'string' ? diag.code : String(diag.code);
    try {
        const result = await mcpManager.client.callTool('explain_diagnostic', { code });
        const content = result.content?.[0]?.text;
        if (content) {
            const parsed = JSON.parse(content);
            if (parsed.error) {
                vscode.window.showWarningMessage(parsed.error);
                return;
            }
            const md = new vscode.MarkdownString(
                `### ${parsed.title}\n\n` +
                `${parsed.description}\n\n` +
                `**Cause:** ${parsed.cause}\n\n` +
                `**Fix:** ${parsed.fix}`
            );
            if (parsed.example) {
                md.appendMarkdown(
                    `\n\n**Bad:**\n\`\`\`ailang\n${parsed.example.bad}\n\`\`\`\n\n` +
                    `**Good:**\n\`\`\`ailang\n${parsed.example.good}\n\`\`\``
                );
            }
            vscode.window.showInformationMessage(md.value, { modal: true });
        }
    } catch (err) {
        vscode.window.showErrorMessage(`MCP explain failed: ${err.message}`);
    }
}

async function insertExample() {
    if (!mcpManager || !mcpManager.isRunning) {
        vscode.window.showWarningMessage('AILang MCP server is not running');
        return;
    }
    const categories = ['hello', 'inventory', 'csv', 'json', 'recursion', 'file_io'];
    const selected = await vscode.window.showQuickPick(categories, {
        placeHolder: 'Select an example to insert',
    });
    if (!selected) return;

    try {
        const result = await mcpManager.client.callTool('get_examples', { category: selected });
        const content = result.content?.[0]?.text;
        if (content) {
            const parsed = JSON.parse(content);
            const code = parsed.code || parsed.example?.code || '';
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const position = editor.selection.active;
                await editor.edit(editBuilder => {
                    editBuilder.insert(position, code);
                });
            }
        }
    } catch (err) {
        vscode.window.showErrorMessage(`MCP insert example failed: ${err.message}`);
    }
}

function activate(context) {
    logger = new Logger('AILang MCP');

    // --- LSP Client ---
    const lspServerOptions = {
        command: 'ail',
        args: ['lsp'],
    };
    const lspClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'ailang' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.ail'),
        },
    };

    lspClient = new LanguageClient(
        'ailangLanguageServer',
        'AILang Language Server',
        lspServerOptions,
        lspClientOptions
    );
    lspClient.start();
    context.subscriptions.push(lspClient);

    // --- Status Bar ---
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'ailang.showOutput';
    statusBarItem.text = '$(robot) AILang MCP: Stopped';
    statusBarItem.tooltip = 'AILang MCP server status — click to show output';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // --- MCP Manager ---
    const config = getConfig();
    mcpManager = new MCPManager(logger, config);

    mcpManager.on('stateChange', (state) => {
        updateStatusBar(state);
    });

    mcpManager.on('failed', (reason) => {
        logger.error(`MCP failed: ${reason}`);
    });

    mcpManager.on('reconnected', () => {
        logger.info('MCP reconnected successfully');
    });

    // --- Commands ---
    context.subscriptions.push(
        vscode.commands.registerCommand('ailang.mcp.start', startMCP),
        vscode.commands.registerCommand('ailang.mcp.stop', stopMCP),
        vscode.commands.registerCommand('ailang.mcp.restart', restartMCP),
        vscode.commands.registerCommand('ailang.mcp.compile', compileCurrentFile),
        vscode.commands.registerCommand('ailang.mcp.explainDiagnostic', explainDiagnostic),
        vscode.commands.registerCommand('ailang.mcp.insertExample', insertExample),
        vscode.commands.registerCommand('ailang.showOutput', () => logger.show())
    );

    // --- Auto-start MCP ---
    if (config.autoStart) {
        startMCP();
    }

    logger.info('AILang extension activated');
}

async function deactivate() {
    if (mcpManager) {
        await mcpManager.dispose();
        mcpManager = null;
    }
    if (logger) {
        logger.dispose();
        logger = null;
    }
    if (lspClient) {
        await lspClient.stop();
        lspClient = null;
    }
}

module.exports = { activate, deactivate };
