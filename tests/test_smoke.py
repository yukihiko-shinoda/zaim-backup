"""Smoke test: full join path without network or workspace I/O."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

from zaimbackup.zaim.api.cache import ZaimCache
from zaimbackup.zaim.api.joiner import Joiner

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


EXPECTED_AMOUNT = 500


def test_joiner_returns_money_with_joined_fields(
    mock_zaim_api: MagicMock,
    fake_config: MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Joiner resolves category, genre, and account foreign keys into nested objects."""
    monkeypatch.setattr(ZaimCache, "DUMP_MONEY", tmp_path / "money.csv")
    monkeypatch.setattr(ZaimCache, "DUMP_CATEGORIES", tmp_path / "categories.yml")
    monkeypatch.setattr(ZaimCache, "DUMP_GENRES", tmp_path / "genres.yml")
    monkeypatch.setattr(ZaimCache, "DUMP_ACCOUNTS", tmp_path / "accounts.yml")

    with patch("zaimbackup.zaim.api.cache.ZaimApi", return_value=mock_zaim_api):
        joiner = Joiner(fake_config)
        money = next(joiner.list_money)

    assert money.amount == EXPECTED_AMOUNT
    assert money.to_account is None  # to_account_id=0 is falsy → None
    assert money.category is not None
    assert money.genre is not None
    assert money.from_account is not None
    assert (money.category["name"], money.genre["name"], money.from_account["name"]) == ("食費", "外食", "現金")
