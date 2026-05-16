"""Zaim API money."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import TypedDict

from zaimbackup.zaim import JST

if TYPE_CHECKING:
    from zaimbackup.zaim.api.models.account import Account
    from zaimbackup.zaim.api.models.category import Category
    from zaimbackup.zaim.api.models.genre import Genre


class MoneyTypeDef(TypedDict):
    """The model of Zaim API data row."""

    id: int
    user_id: int
    date: str
    mode: str
    category_id: int
    genre_id: int
    from_account_id: int
    to_account_id: int
    amount: int
    comment: str
    active: int
    created: str
    currency_code: str
    name: str
    receipt_id: int
    place_uid: str
    place: str
    original_money_ids: str


@dataclass
class Money:
    """The model of Zaim API data row."""

    id: int
    user_id: int
    date: str
    mode: str
    category_id: int
    genre_id: int
    from_account_id: int
    to_account_id: int
    amount: int
    comment: str
    active: int
    created: str
    currency_code: str
    name: str
    receipt_id: int
    place_uid: str
    place: str
    original_money_ids: str
    category: Category | None = None
    genre: Genre | None = None
    from_account: Account | None = None
    to_account: Account | None = None

    @property
    def date_as_date(self) -> datetime.date:
        """Return the date as a datetime.date object."""
        return datetime.datetime.strptime(self.date, "%Y-%m-%d").astimezone(JST).date()
