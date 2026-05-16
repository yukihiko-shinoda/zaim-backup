"""Parameter TypedDicts for Zaim API update calls."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict

if TYPE_CHECKING:
    # Reason: Pyflake's issue:
    # - False positive F401 in recent version (at least v3.4.0) · Issue #850 · PyCQA/pyflakes
    #   https://github.com/pycqa/pyflakes/issues/850
    from datetime import date  # noqa: F401,RUF100


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
