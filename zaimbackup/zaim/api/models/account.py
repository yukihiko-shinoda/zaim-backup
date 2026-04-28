"""Zaim account."""

from typing import TypedDict

from pyzaim import ZaimAPI

from zaimbackup.config import Config


class Account(TypedDict):
    """The model of Zaim account."""

    id: int
    name: str
    modified: str
    sort: int
    active: int
    local_id: int
    website_id: int
    parent_account_id: int


def accounts() -> dict[str, Account]:
    """Gets the accounts from Zaim."""
    api = ZaimAPI(**Config().api)
    # Reason: No way to avoid this issue. pylint: disable-next=protected-access
    response = api._get_account()  # noqa: SLF001
    dictionary_account = {}
    for account in response["accounts"]:
        if account["active"] == -1:
            continue
        dictionary_account[account["name"]] = account
    for requested in response["requested"]:
        if requested["active"] == -1:
            continue
        dictionary_account[requested["name"]] = requested
    return dictionary_account
