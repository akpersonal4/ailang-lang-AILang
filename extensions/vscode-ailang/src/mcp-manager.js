'use strict';

const { spawn } = require('child_process');
const EventEmitter = require('events');
const { MCPClient } = require('./mcp-client');

/**
 * State machine for MCP server lifecycle.
 *
 * States:
 *   stopped → starting → running → stopped
 *                        running → reconnecting → running
 *                        running → failed
 *   starting → failed
 *   reconnecting → failed (after max attempts)
 */
const State = {
    STOPPED: 'stopped',
    STARTING: 'starting',
    RUNNING: 'running',
    RECONNECTING: 'reconnecting',
    FAILED: 'failed',
};

class MCPManager extends EventEmitter {
    constructor(logger, config) {
        super();
        this.logger = logger;
        this.config = config;
        this._state = State.STOPPED;
        this._client = null;
        this._process = null;
        this._reconnectAttempts = 0;
        this._maxReconnectAttempts = config.maxReconnectAttempts || 3;
        this._reconnectTimer = null;
    }

    get state() {
        return this._state;
    }

    get client() {
        return this._client;
    }

    get isRunning() {
        return this._state === State.RUNNING;
    }

    _setState(newState) {
        const old = this._state;
        this._state = newState;
        this.logger.info(`State: ${old} → ${newState}`);
        this.emit('stateChange', newState, old);
    }

    /**
     * Start the MCP server process.
     * @returns {Promise<MCPClient>} The initialized client
     */
    async start() {
        if (this._state === State.RUNNING || this._state === State.STARTING) {
            this.logger.info('Server already running or starting');
            return this._client;
        }

        this._setState(State.STARTING);
        this._reconnectAttempts = 0;

        try {
            await this._spawn();
            return this._client;
        } catch (err) {
            this._setState(State.FAILED);
            throw err;
        }
    }

    /**
     * Stop the MCP server process.
     */
    async stop() {
        if (this._state === State.STOPPED) {
            return;
        }

        this.logger.info('Stopping MCP server...');
        this._clearReconnectTimer();

        if (this._client) {
            this._client.dispose();
            this._client = null;
        }

        if (this._process && !this._process.killed) {
            this._process.kill();
            this._process = null;
        }

        this._setState(State.STOPPED);
    }

    /**
     * Restart the MCP server.
     * @returns {Promise<MCPClient>}
     */
    async restart() {
        await this.stop();
        return this.start();
    }

    /**
     * Spawn the MCP server process and initialize the client.
     */
    async _spawn() {
        const command = this.config.command || 'ail';
        const args = this.config.args || ['mcp'];
        const timeout = this.config.timeout || 30000;

        this.logger.info(`Spawning: ${command} ${args.join(' ')}`);

        const child = spawn(command, args, {
            stdio: ['pipe', 'pipe', 'pipe'],
            shell: process.platform === 'win32',
        });

        this._process = child;
        this._client = new MCPClient(child, this.logger);

        this._client.on('exit', (code) => {
            if (this._state === State.RUNNING) {
                this._attemptReconnect();
            }
        });

        this._client.on('error', (err) => {
            this.logger.error(`Client error: ${err.message}`);
        });

        await this._client.initialize(timeout);
        this._setState(State.RUNNING);
        return this._client;
    }

    /**
     * Attempt to reconnect after an unexpected exit.
     */
    _attemptReconnect() {
        if (this._reconnectAttempts >= this._maxReconnectAttempts) {
            this.logger.error(`Max reconnect attempts (${this._maxReconnectAttempts}) reached`);
            this._setState(State.FAILED);
            this.emit('failed', 'Max reconnect attempts reached');
            return;
        }

        this._reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this._reconnectAttempts - 1), 10000);
        this._setState(State.RECONNECTING);
        this.logger.info(`Reconnecting in ${delay}ms (attempt ${this._reconnectAttempts}/${this._maxReconnectAttempts})...`);

        this._reconnectTimer = setTimeout(async () => {
            try {
                await this._spawn();
                this._reconnectAttempts = 0;
                this.emit('reconnected');
            } catch (err) {
                this.logger.error(`Reconnect failed: ${err.message}`);
                this._attemptReconnect();
            }
        }, delay);
    }

    _clearReconnectTimer() {
        if (this._reconnectTimer) {
            clearTimeout(this._reconnectTimer);
            this._reconnectTimer = null;
        }
    }

    /**
     * Clean up all resources.
     */
    async dispose() {
        this._clearReconnectTimer();
        await this.stop();
        this.removeAllListeners();
    }
}

module.exports = { MCPManager, State };
