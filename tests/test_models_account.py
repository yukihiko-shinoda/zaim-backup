"""Tests for zaimbackup/zaim/api/models/account.py."""

from typing import cast

from tests.conftest import FAKE_ACCOUNT
from zaimbackup.zaim.api.models.account import Account
from zaimbackup.zaim.api.models.account import accounts


def _make_response(
    account_list: list[Account] | None = None,
    requested_list: list[Account] | None = None,
) -> dict[str, list[Account]]:
    return {
        "accounts": account_list or [],
        "requested": requested_list or [],
    }


def test_accounts_returns_active_keyed_by_name() -> None:
    requested = cast("Account", {**FAKE_ACCOUNT, "name": "クレジットカード"})
    result = accounts(_make_response(account_list=[FAKE_ACCOUNT], requested_list=[requested]))
    assert result == {FAKE_ACCOUNT["name"]: FAKE_ACCOUNT, requested["name"]: requested}


def test_accounts_excludes_inactive() -> None:
    inactive = cast("Account", {**FAKE_ACCOUNT, "active": -1})
    result = accounts(_make_response(account_list=[inactive], requested_list=[inactive]))
    assert not result
