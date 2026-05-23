"""Tests for StaticTokenProvider."""

from __future__ import annotations

import pytest

from gbp_connector import StaticTokenProvider


def test_returns_supplied_token_each_call() -> None:
    provider = StaticTokenProvider("hardcoded-token")
    assert provider.get_access_token() == "hardcoded-token"
    assert provider.get_access_token() == "hardcoded-token"


def test_rejects_empty_token() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        StaticTokenProvider("")


def test_token_is_not_publicly_mutable() -> None:
    """__slots__ means there's no instance __dict__ to inject random attrs into."""
    provider = StaticTokenProvider("t")
    with pytest.raises(AttributeError):
        provider.something_else = "x"  # type: ignore[attr-defined]
