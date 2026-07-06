"""Lexical runtime environments for AILang."""

from __future__ import annotations

from typing import Any


class _CacheStats:
    """Lightweight instrumentation counters (no semantic effect)."""

    __slots__ = ("hits", "misses", "negative_hits")

    def __init__(self) -> None:
        self.hits = 0
        self.misses = 0
        self.negative_hits = 0


class Environment:
    """A lexical runtime scope with parent lookup semantics."""

    def __init__(self, parent: Environment | None = None) -> None:
        self._values: dict[str, Any] = {}
        self._parent = parent
        self._resolve_cache: dict[str, Environment] = {}
        self._cache_stats = _CacheStats()

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value

    def assign(self, name: str, value: Any) -> None:
        if name in self._values:
            self._values[name] = value
            return
        if self._parent is not None:
            self._parent.assign(name, value)
            return
        self.define(name, value)

    def resolve(self, name: str) -> Any:
        cached_env = self._resolve_cache.get(name)
        if cached_env is not None:
            self._cache_stats.hits += 1
            return cached_env._values[name]

        self._cache_stats.misses += 1

        if name in self._values:
            self._resolve_cache[name] = self
            return self._values[name]

        if self._parent is not None:
            if name in self._parent._resolve_cache:
                cached_env = self._parent._resolve_cache[name]
                self._resolve_cache[name] = cached_env
                return cached_env._values[name]

            value = self._parent.resolve(name)
            if name in self._parent._resolve_cache:
                self._resolve_cache[name] = self._parent._resolve_cache[name]
            return value

        self._cache_stats.negative_hits += 1
        raise NameError(f"Undefined variable: {name}")

    def get_cache_info(self) -> dict[str, Any]:
        return {
            "cache_size": len(self._resolve_cache),
            "entries": list(self._resolve_cache.keys()),
        }

    @property
    def values(self) -> dict[str, Any]:
        return self._values
