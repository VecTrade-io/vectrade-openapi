"""Shared fixtures for spec validation tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def spec() -> dict:
    """Load and parse spec.yaml."""
    with open(ROOT / "spec.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def asyncapi() -> dict:
    """Load and parse asyncapi.yaml."""
    with open(ROOT / "asyncapi.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def spectral() -> dict:
    """Load and parse .spectral.yaml."""
    with open(ROOT / ".spectral.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def spec_raw() -> str:
    """Raw text content of spec.yaml."""
    return (ROOT / "spec.yaml").read_text()


@pytest.fixture(scope="session")
def asyncapi_raw() -> str:
    """Raw text content of asyncapi.yaml."""
    return (ROOT / "asyncapi.yaml").read_text()


def _collect_operations(spec: dict) -> list[tuple[str, str, dict]]:
    """Return (method, path, operation) tuples for every operation."""
    ops = []
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method.startswith("x-") or not isinstance(op, dict):
                continue
            ops.append((method, path, op))
    return ops


@pytest.fixture(scope="session")
def operations(spec: dict) -> list[tuple[str, str, dict]]:
    """All (method, path, operation) tuples."""
    return _collect_operations(spec)


def _resolve_ref(spec: dict, ref: str) -> object | None:
    """Resolve a JSON Pointer $ref within the spec. Returns None if broken."""
    if not ref.startswith("#/"):
        return None
    parts = ref[2:].split("/")
    node = spec
    for part in parts:
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


@pytest.fixture(scope="session")
def resolve(spec: dict):
    """Return a resolver function bound to the spec."""
    def _resolve(ref: str):
        return _resolve_ref(spec, ref)
    return _resolve
