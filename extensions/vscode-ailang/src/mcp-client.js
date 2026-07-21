'use strict';

const EventEmitter = require('events');

/**
 * JSON-RPC 2.0 client over newline-delimited JSON (NDJSON).
 *
 * Communicates with the AILang MCP server via stdin/stdout.
 * Each message is a single JSON object followed by a newline.
 */
class MCPClient extends EventEmitter {
    constructor(process, logger) {
        super();
        this.process = process;
        this.logger = logger;
        this._nextId = 1;
        this._pending = new Map();
        this._buffer = '';
        this._initialized = false;
        this._tools = [];

        this._setupStdout();
        this._setupStderr();
        this._setupExit();
    }

    _setupStdout() {
        this.process.stdout.setEncoding('utf8');
        this.process.stdout.on('data', (data) => {
            this._buffer += data;
            const lines = this._buffer.split('\n');
            this._buffer = lines.pop();
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed) {
                    this._onMessage(trimmed);
                }
            }
        });
    }

    _setupStderr() {
        this.process.stderr.setEncoding('utf8');
        this.process.stderr.on('data', (data) => {
            const text = data.toString().trim();
            if (text) {
                this.logger.info(`[server] ${text}`);
            }
        });
    }

    _setupExit() {
        this.process.on('exit', (code, signal) => {
            this.logger.info(`Server exited (code=${code}, signal=${signal})`);
            this._rejectAllPending(new Error(`Server exited with code ${code}`));
            this._initialized = false;
            this.emit('exit', code, signal);
        });

        this.process.on('error', (err) => {
            this.logger.error(`Process error: ${err.message}`);
            this._rejectAllPending(err);
            this.emit('error', err);
        });
    }

    _onMessage(raw) {
        let msg;
        try {
            msg = JSON.parse(raw);
        } catch (err) {
            this.logger.error(`Invalid JSON: ${raw.substring(0, 100)}`);
            return;
        }

        if (msg.id !== undefined && this._pending.has(msg.id)) {
            const { resolve, reject, timer } = this._pending.get(msg.id);
            clearTimeout(timer);
            this._pending.delete(msg.id);

            if (msg.error) {
                const err = new Error(msg.error.message || 'MCP error');
                err.code = msg.error.code;
                reject(err);
            } else {
                resolve(msg.result);
            }
        } else if (msg.method) {
            this.emit('notification', msg.method, msg.params);
        }
    }

    _rejectAllPending(err) {
        for (const [id, { reject, timer }] of this._pending) {
            clearTimeout(timer);
            reject(err);
        }
        this._pending.clear();
    }

    _send(msg) {
        const json = JSON.stringify(msg);
        this.process.stdin.write(json + '\n');
    }

    _request(method, params, timeout) {
        return new Promise((resolve, reject) => {
            const id = this._nextId++;
            const timer = setTimeout(() => {
                this._pending.delete(id);
                reject(new Error(`Request ${method} timed out after ${timeout}ms`));
            }, timeout);

            this._pending.set(id, { resolve, reject, timer });
            this._send({ jsonrpc: '2.0', id, method, params: params || {} });
        });
    }

    /**
     * Perform MCP initialization handshake.
     * Sends `initialize` then `tools/list`.
     * Resolves with { serverInfo, tools }.
     */
    async initialize(timeout = 30000) {
        this.logger.info('Initializing MCP connection...');

        const result = await this._request('initialize', {}, timeout);
        this.logger.info(`Server: ${result.serverInfo?.name} v${result.serverInfo?.version}`);

        const toolsResult = await this._request('tools/list', {}, timeout);
        this._tools = toolsResult.tools || [];
        this._initialized = true;

        this.logger.info(`MCP ready — ${this._tools.length} tools available`);
        return { serverInfo: result.serverInfo, tools: this._tools };
    }

    /**
     * Check if the client has completed initialization.
     */
    get isInitialized() {
        return this._initialized;
    }

    /**
     * Get the list of available tools (from last initialize).
     */
    get tools() {
        return this._tools;
    }

    /**
     * Invoke an MCP tool by name.
     * @param {string} name - Tool name
     * @param {object} args - Tool arguments
     * @param {number} timeout - Timeout in ms
     * @returns {Promise<object>} MCP content result
     */
    async callTool(name, args = {}, timeout = 30000) {
        if (!this._initialized) {
            throw new Error('MCP client not initialized');
        }
        this.logger.info(`callTool: ${name}`);
        const result = await this._request('tools/call', { name, arguments: args }, timeout);
        return result;
    }

    /**
     * List available tools from the server.
     * @param {number} timeout
     * @returns {Promise<Array>} Tool definitions
     */
    async listTools(timeout = 30000) {
        const result = await this._request('tools/list', {}, timeout);
        return result.tools || [];
    }

    /**
     * Send a ping to check liveness.
     * @param {number} timeout
     * @returns {Promise<object>}
     */
    async ping(timeout = 5000) {
        return this._request('ping', {}, timeout);
    }

    /**
     * Clean up the client and kill the server process.
     */
    dispose() {
        this._rejectAllPending(new Error('Client disposed'));
        if (this.process && !this.process.killed) {
            this.process.kill();
        }
        this.removeAllListeners();
    }
}

module.exports = { MCPClient };
