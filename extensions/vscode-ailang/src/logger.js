'use strict';

/**
 * Logger that wraps the MCP client/manager API for testing outside VS Code,
 * and wraps vscode.window.createOutputChannel when running inside VS Code.
 *
 * In test mode (no vscode available), logs go to console.
 */
class Logger {
    constructor(channelName) {
        this._channelName = channelName || 'AILang MCP';
        this._channel = null;
        this._tryCreateChannel();
    }

    _tryCreateChannel() {
        try {
            const vscode = require('vscode');
            this._channel = vscode.window.createOutputChannel(this._channelName);
        } catch {
            this._channel = null;
        }
    }

    _write(level, message) {
        const timestamp = new Date().toISOString();
        const formatted = `[${timestamp}] [${level}] ${message}`;

        if (this._channel) {
            this._channel.appendLine(formatted);
        } else if (level === 'ERROR') {
            console.error(formatted);
        } else {
            console.log(formatted);
        }
    }

    info(message) {
        this._write('INFO', message);
    }

    warn(message) {
        this._write('WARN', message);
    }

    error(message) {
        this._write('ERROR', message);
    }

    debug(message) {
        this._write('DEBUG', message);
    }

    /**
     * Get the underlying VS Code OutputChannel (if available).
     * @returns {object|null}
     */
    get channel() {
        return this._channel;
    }

    /**
     * Show the output channel to the user.
     */
    show() {
        if (this._channel) {
            this._channel.show();
        }
    }

    /**
     * Clean up the output channel.
     */
    dispose() {
        if (this._channel) {
            this._channel.dispose();
            this._channel = null;
        }
    }
}

module.exports = { Logger };
