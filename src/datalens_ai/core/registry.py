"""Plugin registry for providers and chart types."""

from __future__ import annotations

from typing import Any

_providers: dict[str, type] = {}
_chart_types: dict[str, type] = {}


def register_provider(name: str):
    """Decorator to register an AI provider."""
    def decorator(cls):
        _providers[name] = cls
        return cls
    return decorator


def register_chart_type(name: str):
    """Decorator to register a chart type."""
    def decorator(cls):
        _chart_types[name] = cls
        return cls
    return decorator


def get_provider(name: str, **kwargs: Any):
    """Get a registered provider by name."""
    if name not in _providers:
        available = list(_providers.keys())
        raise KeyError(f"Unknown provider: {name}. Available: {available}")
    return _providers[name](**kwargs)


def get_chart_type(name: str):
    """Get a registered chart type by name."""
    if name not in _chart_types:
        available = list(_chart_types.keys())
        raise KeyError(f"Unknown chart type: {name}. Available: {available}")
    return _chart_types[name]


def list_providers() -> list[str]:
    """List registered provider names."""
    return list(_providers.keys())


def list_chart_types() -> list[str]:
    """List registered chart type names."""
    return list(_chart_types.keys())
