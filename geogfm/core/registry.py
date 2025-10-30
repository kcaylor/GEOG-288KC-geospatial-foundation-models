# geogfm.core.registry — Minimal name→builder registry for models/heads (Week 7).
# Tangled on 2025-10-30T16:29:26

from __future__ import annotations
from typing import Callable, Dict, Any

class Registry:
    """Minimal name → builder registry for models/heads."""
    def __init__(self) -> None:
        self._fns: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
            key = name.lower()
            if key in self._fns:
                raise KeyError(f"Duplicate registration: {key}")
            self._fns[key] = fn
            return fn
        return wrapper

    def build(self, name: str, *args, **kwargs):
        key = name.lower()
        if key not in self._fns:
            raise KeyError(f"Unknown name: {name}")
        return self._fns[key](*args, **kwargs)

MODEL_REGISTRY = Registry()
HEAD_REGISTRY = Registry()
