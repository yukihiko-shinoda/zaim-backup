"""Tests for zaimbackup/zaim/api/models/account.py."""

from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

from zaimbackup.zaim.api.models.account import accounts

_ACCOUNT: dict[str, Any] = {
    "id": 100,
    "name": "現金",
    "modified": "2024-01-01",
    "sort": 1,
    "active": 1,
    "local_id": 0,
    "website_id": 0,
    "parent_account_id": 0,
}


def _make_response(
    account_list: list[dict[str, Any]] | None = None,
    requested_list: list[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    return {
        "accounts": account_list or [],
        "requested": requested_list or [],
    }


def test_accounts_returns_active_keyed_by_name(fake_config: MagicMock) -> None:
    requested = {**_ACCOUNT, "name": "クレジットカード"}
    mock_api = MagicMock()
    mock_api._get_account.return_value = _make_response(
        account_list=[_ACCOUNT],
        requested_list=[requested],
    )
    with (
        patch("zaimbackup.zaim.api.models.account.ZaimAPI", return_value=mock_api),
        patch("zaimbackup.zaim.api.models.account.Config", return_value=fake_config),
    ):
        result = accounts()
    assert result == {_ACCOUNT["name"]: _ACCOUNT, requested["name"]: requested}


def test_accounts_excludes_inactive(fake_config: MagicMock) -> None:
    inactive = {**_ACCOUNT, "active": -1}
    mock_api = MagicMock()
    mock_api._get_account.return_value = _make_response(
        account_list=[inactive],
        requested_list=[inactive],
    )
    with (
        patch("zaimbackup.zaim.api.models.account.ZaimAPI", return_value=mock_api),
        patch("zaimbackup.zaim.api.models.account.Config", return_value=fake_config),
    ):
        result = accounts()
    assert result == {}
