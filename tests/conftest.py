"""Shared fixtures and fake data for zaimbackup tests."""

from unittest.mock import MagicMock

import pytest

from zaimbackup.zaim.api.models.account import Account
from zaimbackup.zaim.api.models.category import Category
from zaimbackup.zaim.api.models.genre import Genre
from zaimbackup.zaim.api.models.money import MoneyTypeDef

FAKE_CATEGORY: Category = {
    "id": 1,
    "name": "食費",
    "mode": "payment",
    "sort": 1,
    "parent_category_id": 0,
    "active": 1,
    "modified": "2024-01-01",
}
FAKE_GENRE: Genre = {"id": 10, "category_id": 1, "name": "外食"}
FAKE_ACCOUNT: Account = {
    "id": 100,
    "name": "現金",
    "modified": "2024-01-01",
    "sort": 1,
    "active": 1,
    "local_id": 0,
    "website_id": 0,
    "parent_account_id": 0,
}
FAKE_MONEY: MoneyTypeDef = {
    "id": 1,
    "user_id": 99,
    "date": "2024-01-15",
    "mode": "payment",
    "category_id": 1,
    "genre_id": 10,
    "from_account_id": 100,
    "to_account_id": 0,
    "amount": 500,
    "comment": "",
    "active": 1,
    "created": "2024-01-15 00:00:00",
    "currency_code": "JPY",
    "name": "",
    "receipt_id": 0,
    "place_uid": "",
    "place": "",
    "original_money_ids": "",
}


@pytest.fixture
def mock_zaim_api() -> MagicMock:
    """MagicMock standing in for ZaimApi; returns one row of fake data."""
    mock = MagicMock()
    mock.get_categories.return_value = [FAKE_CATEGORY]
    mock.get_genres.return_value = [FAKE_GENRE]
    mock.get_accounts.return_value = [FAKE_ACCOUNT]
    mock.get_data.return_value = [dict(FAKE_MONEY)]
    return mock


@pytest.fixture
def fake_config() -> MagicMock:
    """MagicMock standing in for Config; carries the expected .api shape."""
    cfg = MagicMock()
    cfg.api = {
        "consumer_id": "fake",
        "consumer_secret": "fake",  # nosec: B105 -- fake credentials
        "access_token": "fake",
        "access_token_secret": "fake",
        "oauth_verifier": "fake",
    }
    return cfg
