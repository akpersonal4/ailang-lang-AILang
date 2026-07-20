"""LSP server — main JSON-RPC server for the AILang language server."""

from __future__ import annotations

from typing import Any

from compiler.lsp.documents import Document
from compiler.lsp.features.code_actions import get_code_actions
from compiler.lsp.features.completion import get_completions
from compiler.lsp.features.definition import get_definition
from compiler.lsp.features.diagnostics import get_diagnostics
from compiler.lsp.features.hover import get_hover
from compiler.lsp.features.references import get_references
from compiler.lsp.features.rename import get_rename_edits
from compiler.lsp.features.signature_help import get_signature_help
from compiler.lsp.features.symbols import get_document_symbols
from compiler.lsp.features.workspace_symbols import get_workspace_symbols
from compiler.lsp.protocol import _read_message, _send_message


class LspServer:
    """AILang Language Server Protocol implementation."""

    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self._initialize_params: dict[str, Any] | None = None
        self._capabilities: dict[str, Any] | None = None
        self._shutdown_received = False

    def _get_document(self, uri: str) -> Document:
        if uri not in self.documents:
            self.documents[uri] = Document(uri, "")
        return self.documents[uri]

    def run(self) -> None:
        """Main loop: read messages from stdin and dispatch."""
        while True:
            msg = _read_message()
            if msg is None:
                break
            self._handle_message(msg)
            if self._shutdown_received:
                break

    def _handle_message(self, msg: dict[str, Any]) -> None:
        method = msg.get("method")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        if method:
            result = self._handle_method(method, params)
            if msg_id is not None:
                _send_message({"jsonrpc": "2.0", "id": msg_id, "result": result})

    def _handle_method(self, method: str, params: dict[str, Any]) -> Any:
        handlers = {
            "initialize": self._handle_initialize,
            "shutdown": self._handle_shutdown,
            "exit": self._handle_exit,
            "textDocument/didOpen": self._handle_did_open,
            "textDocument/didChange": self._handle_did_change,
            "textDocument/didSave": self._handle_did_save,
            "textDocument/didClose": self._handle_did_close,
            "textDocument/completion": self._handle_completion,
            "completionItem/resolve": self._handle_completion_resolve,
            "textDocument/hover": self._handle_hover,
            "textDocument/definition": self._handle_definition,
            "textDocument/references": self._handle_references,
            "textDocument/rename": self._handle_rename,
            "textDocument/signatureHelp": self._handle_signature_help,
            "textDocument/documentSymbol": self._handle_document_symbols,
            "textDocument/codeAction": self._handle_code_action,
            "workspace/symbol": self._handle_workspace_symbols,
        }
        handler = handlers.get(method)
        if handler is not None:
            return handler(params)
        return None

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        self._initialize_params = params
        self._capabilities = {
            "textDocumentSync": {
                "openClose": True,
                "change": 2,  # Incremental
                "save": {"includeText": False},
            },
            "completionProvider": {
                "triggerCharacters": [".", "("],
                "resolveProvider": True,
            },
            "hoverProvider": True,
            "definitionProvider": True,
            "referencesProvider": True,
            "renameProvider": True,
            "signatureHelpProvider": {
                "triggerCharacters": ["("],
            },
            "documentSymbolProvider": True,
            "workspaceSymbolProvider": True,
            "codeActionProvider": True,
        }
        return {
            "capabilities": self._capabilities,
            "serverInfo": {
                "name": "ailang-lsp",
                "version": "0.2.0",
            },
        }

    def _handle_shutdown(self, params: dict[str, Any]) -> None:
        self._shutdown_received = True

    def _handle_exit(self, params: dict[str, Any]) -> None:
        pass

    # -----------------------------------------------------------------------
    # Text document sync
    # -----------------------------------------------------------------------

    def _handle_did_open(self, params: dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        text = text_doc.get("text", "")
        doc = Document(uri, text)
        self.documents[uri] = doc
        doc.compile()
        self._publish_diagnostics(uri)

    def _handle_did_change(self, params: dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        content_changes = params.get("contentChanges", [])
        doc = self._get_document(uri)

        for change in content_changes:
            text = change.get("text", "")
            doc.text = text

        doc.compile()
        self._publish_diagnostics(uri)

    def _handle_did_save(self, params: dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        doc = self._get_document(uri)
        doc.ensure_compiled()
        self._publish_diagnostics(uri)

    def _handle_did_close(self, params: dict[str, Any]) -> None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        self.documents.pop(uri, None)

    # -----------------------------------------------------------------------
    # Diagnostics notification
    # -----------------------------------------------------------------------

    def _publish_diagnostics(self, uri: str) -> None:
        doc = self.documents.get(uri)
        if doc is None:
            return
        diagnostics = get_diagnostics(doc)
        _send_message(
            {
                "jsonrpc": "2.0",
                "method": "textDocument/publishDiagnostics",
                "params": {"uri": uri, "diagnostics": diagnostics},
            }
        )

    # -----------------------------------------------------------------------
    # Features
    # -----------------------------------------------------------------------

    def _handle_completion(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        position = params.get("position", {})
        doc = self._get_document(uri)
        items = get_completions(doc, position)
        return items

    def _handle_completion_resolve(self, params: dict[str, Any]) -> dict[str, Any]:
        return params

    def _handle_hover(self, params: dict[str, Any]) -> dict[str, Any] | None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        position = params.get("position", {})
        doc = self._get_document(uri)
        return get_hover(doc, position)

    def _handle_definition(self, params: dict[str, Any]) -> list[dict[str, Any]] | None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        position = params.get("position", {})
        doc = self._get_document(uri)
        return get_definition(doc, position)

    def _handle_references(self, params: dict[str, Any]) -> list[dict[str, Any]] | None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        position = params.get("position", {})
        doc = self._get_document(uri)
        return get_references(doc, position)

    def _handle_rename(self, params: dict[str, Any]) -> dict[str, Any] | None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        position = params.get("position", {})
        new_name = params.get("newName", "")
        doc = self._get_document(uri)
        return get_rename_edits(doc, position, new_name)

    def _handle_signature_help(self, params: dict[str, Any]) -> dict[str, Any] | None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        position = params.get("position", {})
        doc = self._get_document(uri)
        return get_signature_help(doc, position)

    def _handle_document_symbols(
        self, params: dict[str, Any]
    ) -> list[dict[str, Any]] | None:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        doc = self._get_document(uri)
        return get_document_symbols(doc)

    def _handle_workspace_symbols(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        query = params.get("query", "")
        return get_workspace_symbols(self.documents, query)

    def _handle_code_action(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        text_doc = params.get("textDocument", {})
        uri = text_doc.get("uri", "")
        _range = params.get("range", {})
        context = params.get("context", {})
        doc = self._get_document(uri)
        return get_code_actions(doc, _range, context)
