"""Zaim account."""

from typing import TypedDict


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


def accounts(response: dict[str, list[Account]]) -> dict[str, Account]:
    """Gets the accounts from a raw API response dict."""
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
