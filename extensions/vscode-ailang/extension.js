const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;

function activate(context) {
    const serverOptions = {
        command: 'ail',
        args: ['lsp']
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'ailang' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.ail')
        }
    };

    client = new LanguageClient(
        'ailangLanguageServer',
        'AILang Language Server',
        serverOptions,
        clientOptions
    );
    client.start();
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
