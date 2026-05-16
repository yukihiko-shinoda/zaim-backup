"""Smoke test: full join path without network or workspace I/O."""

from unittest.mock import patch

from zaimbackup.zaim.api.cache import ZaimCache
from zaimbackup.zaim.api.joiner import Joiner


def test_joiner_returns_money_with_joined_fields(
    mock_zaim_api,
    fake_config,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(ZaimCache, "DUMP_MONEY", tmp_path / "money.csv")
    monkeypatch.setattr(ZaimCache, "DUMP_CATEGORIES", tmp_path / "categories.yml")
    monkeypatch.setattr(ZaimCache, "DUMP_GENRES", tmp_path / "genres.yml")
    monkeypatch.setattr(ZaimCache, "DUMP_ACCOUNTS", tmp_path / "accounts.yml")

    with patch("zaimbackup.zaim.api.cache.ZaimApi", return_value=mock_zaim_api):
        joiner = Joiner(fake_config)
        money = next(joiner.list_money)

    assert money.amount == 500
    assert money.category is not None and money.category["name"] == "食費"
    assert money.genre is not None and money.genre["name"] == "外食"
    assert money.from_account is not None and money.from_account["name"] == "現金"
    assert money.to_account is None  # to_account_id=0 is falsy → None
