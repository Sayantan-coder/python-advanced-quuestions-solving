from __future__ import annotations

import warnings
import functools
from dataclasses import dataclass, field
from graphlib import TopologicalSorter, CycleError
from typing import Any, Callable, Optional


class VersionConflictError(Exception):
    pass


class DependencyError(Exception):
    pass


class CircularDependencyError(Exception):
    pass


@dataclass
class PluginEntry:
    name: str
    version: str
    category: str
    tags: list[str]
    depends_on: list[str]
    obj: Any


class Registry:

    _instance: Optional["Registry"] = None
    _plugins: dict[str, PluginEntry] = {}

    def __new__(cls) -> "Registry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(
        self,
        obj: Any,
        *,
        name: str,
        version: str,
        category: str,
        tags: list[str],
        depends_on: list[str],
    ) -> Any:

        if name in self._plugins:
            existing = self._plugins[name]
            if existing.version != version:
                raise VersionConflictError(
                    f"Plugin '{name}' is already registered with version "
                    f"'{existing.version}', cannot register version '{version}'."
                )

            return obj

        entry = PluginEntry(
            name=name,
            version=version,
            category=category,
            tags=tags,
            depends_on=depends_on,
            obj=obj,
        )
        self._plugins[name] = entry
        return obj

    def lookup(self, name: str) -> PluginEntry:

        try:
            return self._plugins[name]
        except KeyError:
            raise KeyError(f"No plugin named '{name}' is registered.") from None

    def filter_by_category(self, category: str) -> list[PluginEntry]:

        return [p for p in self._plugins.values() if p.category == category]

    def filter_by_tags(self, *tags: str, match_all: bool = False) -> list[PluginEntry]:

        tag_set = set(tags)
        results = []
        for p in self._plugins.values():
            plugin_tags = set(p.tags)
            if match_all:
                if tag_set.issubset(plugin_tags):
                    results.append(p)
            else:
                if tag_set & plugin_tags:
                    results.append(p)
        return results

    def validate_dependencies(self) -> None:

        for plugin in self._plugins.values():
            for dep_name in plugin.depends_on:
                if dep_name not in self._plugins:
                    raise DependencyError(
                        f"Plugin '{plugin.name}' depends on '{dep_name}', "
                        f"which is not registered."
                    )

    def get_ordered(self) -> list[PluginEntry]:

        self.validate_dependencies()

        graph: dict[str, set[str]] = {
            name: set(entry.depends_on) for name, entry in self._plugins.items()
        }

        try:
            sorter = TopologicalSorter(graph)
            ordered_names = list(sorter.static_order())
        except CycleError as exc:
            raise CircularDependencyError(
                f"Circular dependency detected: {exc}"
            ) from exc

        return [self._plugins[name] for name in ordered_names]

    def all_plugins(self) -> list[PluginEntry]:
        return list(self._plugins.values())

    def clear(self) -> None:

        self._plugins.clear()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Registry plugins={list(self._plugins.keys())}>"


_registry = Registry()


def register(
    category: str,
    name: str,
    version: str,
    tags: list[str] | None = None,
    depends_on: list[str] | None = None,
) -> Callable:

    def decorator(obj: Any) -> Any:
        _registry.register(
            obj,
            name=name,
            version=version,
            category=category,
            tags=tags or [],
            depends_on=depends_on or [],
        )

        return obj

    return decorator


def deprecated(replaced_by: str, removal_version: str) -> Callable:

    def decorator(func: Callable) -> Callable:
        _warned: set[int] = set()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if id(func) not in _warned:
                _warned.add(id(func))
                warnings.warn(
                    f"'{func.__name__}' is deprecated and will be removed in "
                    f"version {removal_version}. Use '{replaced_by}' instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
            return func(*args, **kwargs)

        wrapper._is_deprecated = True
        wrapper._replaced_by = replaced_by
        wrapper._removal_version = removal_version
        return wrapper

    return decorator


if __name__ == "__main__":
    import warnings as _w

    _w.simplefilter("always", DeprecationWarning)

    @register("auth", "base_auth", "1.0.0", tags=["security", "core"])
    def base_auth(token: str) -> bool:
        return bool(token)

    @register(
        "auth",
        "jwt_plugin",
        "2.0.0",
        tags=["security", "jwt"],
        depends_on=["base_auth"],
    )
    def jwt_auth(token: str) -> bool:
        return token.startswith("Bearer ")

    @register(
        "db",
        "postgres_plugin",
        "1.5.0",
        tags=["database", "sql"],
        depends_on=["base_auth"],
    )
    class PostgresAdapter:
        def connect(self): ...

    @register(
        "cache",
        "redis_plugin",
        "1.0.0",
        tags=["cache", "fast"],
        depends_on=["postgres_plugin", "jwt_plugin"],
    )
    def redis_cache(key: str) -> None: ...

    @deprecated(replaced_by="jwt_auth", removal_version="3.0.0")
    def old_token_auth(token: str) -> bool:
        return len(token) > 0

    old_token_auth("abc")
    old_token_auth("abc")
    old_token_auth("abc")

    print("\n── Lookup 'jwt_plugin' ──")
    entry = _registry.lookup("jwt_plugin")
    print(
        f"  name={entry.name}, version={entry.version}, "
        f"category={entry.category}, tags={entry.tags}"
    )

    print("\n── filter_by_category('auth') ──")
    for p in _registry.filter_by_category("auth"):
        print(f"  {p.name} v{p.version}")

    print("\n── filter_by_tags('security') ──")
    for p in _registry.filter_by_tags("security"):
        print(f"  {p.name}")

    print("\n── get_ordered() (dependency-resolved) ──")
    for p in _registry.get_ordered():
        deps = p.depends_on or "none"
        print(f"  {p.name:<20} depends_on={deps}")

    print("\n── Version conflict demo ──")
    try:

        @register("auth", "jwt_plugin", "9.9.9")
        def jwt_v2(): ...

    except VersionConflictError as exc:
        print(f"  Caught: {exc}")

    print("\n── Missing dependency demo ──")
    try:

        @register("misc", "orphan_plugin", "1.0.0", depends_on=["nonexistent"])
        def orphan(): ...

        _registry.validate_dependencies()
    except DependencyError as exc:
        print(f"  Caught: {exc}")
