from datetime import date
from typing import TypedDict


class ParameterTransfer(TypedDict):
    data_id: int
    date: date
    amount: int
    from_account_id: int
    to_account_id: int
    comment: str


class ParameterPayment(TypedDict):
    data_id: int
    date: date
    amount: int
    category_id: int | None
    genre_id: int | None
    from_account_id: int
    comment: str
    name: str
    place: str


class ParameterIncome(TypedDict):
    data_id: int
    date: date
    category_id: int | None
    amount: int
    to_account_id: int
    comment: str
    place: str
