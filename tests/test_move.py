"""Tests for zaimbackup/move.py: AbstractMove subclasses and Move orchestrator."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import cast
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from tests.conftest import FAKE_ACCOUNT
from tests.conftest import FAKE_CATEGORY
from tests.conftest import FAKE_GENRE
from tests.conftest import FAKE_MONEY
from zaimbackup.move import Move
from zaimbackup.move import MoveIncome
from zaimbackup.move import MovePayment
from zaimbackup.move import MoveTransfer
from zaimbackup.zaim.api.models.money import Money

if TYPE_CHECKING:
    from zaimbackup.zaim.api.models.account import Account

FAKE_ACCOUNT_OTHER: Account = cast("Account", {**FAKE_ACCOUNT, "id": 200, "name": "銀行"})
FAKE_ACCOUNT_THIRD: Account = cast("Account", {**FAKE_ACCOUNT, "id": 999, "name": "Other", "sort": 2})
EXPECTED_DATE = datetime.date(2024, 1, 15)


def _make_money(**overrides: object) -> Money:
    defaults: dict[str, Any] = {
        **FAKE_MONEY,
        "comment": "test comment",
        "name": "shop name",
        "place": "place name",
        "category": dict(FAKE_CATEGORY),
        "genre": dict(FAKE_GENRE),
        "from_account": dict(FAKE_ACCOUNT),
        "to_account": None,
    }
    defaults.update(overrides)
    return Money(**defaults)


# ---------------------------------------------------------------------------
# MoveTransfer
# ---------------------------------------------------------------------------


def test_move_transfer_build_parameters_returns_correct_dict() -> None:
    """build_parameters maps Money fields to ParameterTransfer with account replacement."""
    money = _make_money(
        mode="transfer",
        from_account=dict(FAKE_ACCOUNT),
        to_account=dict(FAKE_ACCOUNT_OTHER),
    )
    mover = MoveTransfer(MagicMock(), 100, 200)
    result = mover.build_parameters(money)
    assert result == {
        "data_id": 1,
        "date": EXPECTED_DATE,
        "amount": 500,
        "from_account_id": 200,
        "to_account_id": 200,
        "comment": "test comment",
    }


def test_move_transfer_build_parameters_replaces_from_account_id() -> None:
    """from_account_id is replaced when it matches account_to_be_replaced."""
    money = _make_money(
        mode="transfer",
        from_account=dict(FAKE_ACCOUNT),
        to_account=dict(FAKE_ACCOUNT_THIRD),
    )
    result = MoveTransfer(MagicMock(), 100, 200).build_parameters(money)
    assert result["from_account_id"] == FAKE_ACCOUNT_OTHER["id"]
    assert result["to_account_id"] == FAKE_ACCOUNT_THIRD["id"]


def test_move_transfer_build_parameters_replaces_to_account_id() -> None:
    """to_account_id is replaced when it matches account_to_be_replaced."""
    money = _make_money(
        mode="transfer",
        from_account=dict(FAKE_ACCOUNT_THIRD),
        to_account=dict(FAKE_ACCOUNT),
    )
    result = MoveTransfer(MagicMock(), 100, 200).build_parameters(money)
    assert result["from_account_id"] == FAKE_ACCOUNT_THIRD["id"]
    assert result["to_account_id"] == FAKE_ACCOUNT_OTHER["id"]


def test_move_transfer_build_parameters_raises_when_from_account_is_none() -> None:
    money = _make_money(mode="transfer", from_account=None, to_account=dict(FAKE_ACCOUNT))
    with pytest.raises(ValueError, match="Missing account information for transfer"):
        MoveTransfer(MagicMock(), 100, 200).build_parameters(money)


def test_move_transfer_build_parameters_raises_when_to_account_is_none() -> None:
    money = _make_money(mode="transfer", from_account=dict(FAKE_ACCOUNT), to_account=None)
    with pytest.raises(ValueError, match="Missing account information for transfer"):
        MoveTransfer(MagicMock(), 100, 200).build_parameters(money)


def test_move_transfer_call_api_calls_update_transfer() -> None:
    """call_api delegates to zaim_api.update_transfer with the given parameters."""
    mock_api = MagicMock()
    params = {
        "data_id": 1,
        "date": EXPECTED_DATE,
        "amount": 500,
        "from_account_id": 100,
        "to_account_id": 200,
        "comment": "",
    }
    MoveTransfer(mock_api, 100, 200).call_api(params)  # type: ignore[arg-type]
    mock_api.update_transfer.assert_called_once_with(**params)


# ---------------------------------------------------------------------------
# MovePayment
# ---------------------------------------------------------------------------


def test_move_payment_build_parameters_returns_correct_dict() -> None:
    money = _make_money(mode="payment", from_account=dict(FAKE_ACCOUNT))
    result = MovePayment(MagicMock(), 999, 200).build_parameters(money)
    assert result == {
        "data_id": 1,
        "date": EXPECTED_DATE,
        "amount": 500,
        "category_id": 1,
        "genre_id": 10,
        "from_account_id": 100,
        "comment": "test comment",
        "name": "shop name",
        "place": "place name",
    }


def test_move_payment_build_parameters_with_no_category_or_genre() -> None:
    money = _make_money(mode="payment", from_account=dict(FAKE_ACCOUNT), category=None, genre=None)
    result = MovePayment(MagicMock(), 999, 200).build_parameters(money)
    assert result["category_id"] is None
    assert result["genre_id"] is None


def test_move_payment_build_parameters_replaces_from_account_id() -> None:
    money = _make_money(mode="payment", from_account=dict(FAKE_ACCOUNT))
    result = MovePayment(MagicMock(), 100, 200).build_parameters(money)
    assert result["from_account_id"] == FAKE_ACCOUNT_OTHER["id"]


def test_move_payment_build_parameters_raises_when_from_account_is_none() -> None:
    money = _make_money(mode="payment", from_account=None)
    with pytest.raises(ValueError, match="Missing account information for payment"):
        MovePayment(MagicMock(), 100, 200).build_parameters(money)


def test_move_payment_call_api_calls_update_payment() -> None:
    """call_api delegates to zaim_api.update_payment with the given parameters."""
    mock_api = MagicMock()
    params = {
        "data_id": 1,
        "date": EXPECTED_DATE,
        "amount": 500,
        "category_id": 1,
        "genre_id": 10,
        "from_account_id": 100,
        "comment": "",
        "name": "",
        "place": "",
    }
    MovePayment(mock_api, 100, 200).call_api(params)  # type: ignore[arg-type]
    mock_api.update_payment.assert_called_once_with(**params)


# ---------------------------------------------------------------------------
# MoveIncome
# ---------------------------------------------------------------------------


def test_move_income_build_parameters_returns_correct_dict() -> None:
    money = _make_money(mode="income", from_account=None, to_account=dict(FAKE_ACCOUNT))
    result = MoveIncome(MagicMock(), 999, 200).build_parameters(money)
    assert result == {
        "data_id": 1,
        "date": EXPECTED_DATE,
        "category_id": 1,
        "amount": 500,
        "to_account_id": 100,
        "comment": "test comment",
        "place": "place name",
    }


def test_move_income_build_parameters_replaces_to_account_id() -> None:
    money = _make_money(mode="income", from_account=None, to_account=dict(FAKE_ACCOUNT))
    result = MoveIncome(MagicMock(), 100, 200).build_parameters(money)
    assert result["to_account_id"] == FAKE_ACCOUNT_OTHER["id"]


def test_move_income_build_parameters_raises_when_to_account_is_none() -> None:
    money = _make_money(mode="income", from_account=None, to_account=None)
    with pytest.raises(ValueError, match="Missing account information for income"):
        MoveIncome(MagicMock(), 100, 200).build_parameters(money)


def test_move_income_call_api_calls_update_income() -> None:
    """call_api delegates to zaim_api.update_income with the given parameters."""
    mock_api = MagicMock()
    params = {
        "data_id": 1,
        "date": EXPECTED_DATE,
        "category_id": 1,
        "amount": 500,
        "to_account_id": 100,
        "comment": "",
        "place": "",
    }
    MoveIncome(mock_api, 100, 200).call_api(params)  # type: ignore[arg-type]
    mock_api.update_income.assert_called_once_with(**params)


# ---------------------------------------------------------------------------
# Move.move
# ---------------------------------------------------------------------------


def _make_move(fake_config: MagicMock, mock_api: MagicMock) -> Move:
    with (
        patch("zaimbackup.move.ZaimAPI", return_value=mock_api),
        patch("zaimbackup.move.Joiner"),
    ):
        return Move(fake_config, 100, 200)


def test_move_move_skips_when_neither_account_matches(fake_config: MagicMock) -> None:
    """Move() is a no-op when neither from_account nor to_account matches the target ID."""
    mock_api = MagicMock()
    move_obj = _make_move(fake_config, mock_api)
    money = _make_money(
        from_account={
            "id": 999,
            "name": "Other",
            "modified": "2024-01-01",
            "sort": 2,
            "active": 1,
            "local_id": 0,
            "website_id": 0,
            "parent_account_id": 0,
        },
        to_account={
            "id": 888,
            "name": "Another",
            "modified": "2024-01-01",
            "sort": 3,
            "active": 1,
            "local_id": 0,
            "website_id": 0,
            "parent_account_id": 0,
        },
    )
    move_obj.move(money)
    mock_api.update_payment.assert_not_called()
    mock_api.update_transfer.assert_not_called()
    mock_api.update_income.assert_not_called()


def test_move_move_skips_when_from_and_to_account_are_none(fake_config: MagicMock) -> None:
    """Move() is a no-op when both from_account and to_account are None."""
    mock_api = MagicMock()
    move_obj = _make_move(fake_config, mock_api)
    money = _make_money(from_account=None, to_account=None)
    move_obj.move(money)
    mock_api.update_payment.assert_not_called()
    mock_api.update_transfer.assert_not_called()
    mock_api.update_income.assert_not_called()


def test_move_move_dispatches_payment(fake_config: MagicMock) -> None:
    """Move() calls update_payment for payment-mode entries."""
    mock_api = MagicMock()
    move_obj = _make_move(fake_config, mock_api)
    money = _make_money(mode="payment", from_account=dict(FAKE_ACCOUNT))
    move_obj.move(money)
    mock_api.update_payment.assert_called_once()
    mock_api.update_transfer.assert_not_called()
    mock_api.update_income.assert_not_called()


def test_move_move_dispatches_transfer(fake_config: MagicMock) -> None:
    """Move() calls update_transfer for transfer-mode entries."""
    mock_api = MagicMock()
    move_obj = _make_move(fake_config, mock_api)
    money = _make_money(
        mode="transfer",
        from_account=dict(FAKE_ACCOUNT),
        to_account=dict(FAKE_ACCOUNT_OTHER),
    )
    move_obj.move(money)
    mock_api.update_transfer.assert_called_once()
    mock_api.update_payment.assert_not_called()
    mock_api.update_income.assert_not_called()


def test_move_move_dispatches_income(fake_config: MagicMock) -> None:
    """Move() calls update_income for income-mode entries."""
    mock_api = MagicMock()
    move_obj = _make_move(fake_config, mock_api)
    money = _make_money(mode="income", from_account=None, to_account=dict(FAKE_ACCOUNT))
    move_obj.move(money)
    mock_api.update_income.assert_called_once()
    mock_api.update_payment.assert_not_called()
    mock_api.update_transfer.assert_not_called()


# ---------------------------------------------------------------------------
# Move.__call__
# ---------------------------------------------------------------------------


def test_move_call_iterates_list_money(fake_config: MagicMock) -> None:
    """__call__ iterates joiner.list_money and dispatches each entry."""
    mock_api = MagicMock()
    money1 = _make_money(mode="payment", from_account=dict(FAKE_ACCOUNT))
    money2 = _make_money(id=2, mode="income", from_account=None, to_account=dict(FAKE_ACCOUNT))
    with (
        patch("zaimbackup.move.ZaimAPI", return_value=mock_api),
        patch("zaimbackup.move.Joiner") as mock_joiner_cls,
    ):
        mock_joiner_cls.return_value.list_money = iter([money1, money2])
        move_obj = Move(fake_config, 100, 200)
        move_obj()
    assert mock_api.update_payment.call_count == 1
    assert mock_api.update_income.call_count == 1
    mock_api.update_transfer.assert_not_called()
