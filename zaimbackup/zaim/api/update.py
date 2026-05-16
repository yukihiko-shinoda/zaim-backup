"""Parameter TypedDicts for Zaim API update calls."""

# Reason: Maybe Flake8's issue:
# - False positive F401 · Issue #2027 · PyCQA/flake8
#   https://github.com/PyCQA/flake8/issues/2027
from datetime import date  # noqa: F401,RUF100
from typing import TypedDict


class ParameterTransfer(TypedDict):
    """Parameters for updating a transfer entry via the Zaim API."""

    data_id: int
    date: date
    amount: int
    from_account_id: int
    to_account_id: int
    comment: str


class ParameterPayment(TypedDict):
    """Parameters for updating a payment entry via the Zaim API."""

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
    """Parameters for updating an income entry via the Zaim API."""

    data_id: int
    date: date
    category_id: int | None
    amount: int
    to_account_id: int
    comment: str
    place: str
