"""Tests for zaimbackup/move.py: AbstractMove subclasses and Move orchestrator."""

import datetime
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from zaimbackup.move import Move
from zaimbackup.move import MoveIncome
from zaimbackup.move import MovePayment
from zaimbackup.move import MoveTransfer
from zaimbackup.zaim.api.models.money import Money

FAKE_CATEGORY: dict[str, Any] = {
    "id": 1,
    "name": "食費",
    "mode": "payment",
    "sort": 1,
    "parent_category_id": 0,
    "active": 1,
    "modified": "2024-01-01",
}
FAKE_GENRE: dict[str, Any] = {"id": 10, "category_id": 1, "name": "外食"}
FAKE_ACCOUNT: dict[str, Any] = {
    "id": 100,
    "name": "現金",
    "modified": "2024-01-01",
    "sort": 1,
    "active": 1,
    "local_id": 0,
    "website_id": 0,
    "parent_account_id": 0,
}
FAKE_ACCOUNT_OTHER: dict[str, Any] = {**FAKE_ACCOUNT, "id": 200, "name": "銀行"}
EXPECTED_DATE = datetime.date(2024, 1, 15)


def _make_money(**overrides: Any) -> Money:
    defaults: dict[str, Any] = {
        "id": 1,
        "user_id": 99,
        "date": "2024-01-15",
        "mode": "payment",
        "category_id": 1,
        "genre_id": 10,
        "from_account_id": 100,
        "to_account_id": 0,
        "amount": 500,
        "comment": "test comment",
        "active": 1,
        "created": "2024-01-15 00:00:00",
        "currency_code": "JPY",
        "name": "shop name",
        "receipt_id": 0,
        "place_uid": "",
        "place": "place name",
        "original_money_ids": "",
        "category": dict(FAKE_CATEGORY),
        "genre": dict(FAKE_GENRE),
        "from_account": dict(FAKE_ACCOUNT),
        "to_account": None,
    }
    defaults.update(overrides)
    return Money(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# MoveTransfer
# ---------------------------------------------------------------------------


def test_move_transfer_build_parameters_returns_correct_dict() -> None:
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
    money = _make_money(
        mode="transfer",
        from_account=dict(FAKE_ACCOUNT),
        to_account={
            "id": 999,
            "name": "Other",
            "modified": "2024-01-01",
            "sort": 2,
            "active": 1,
            "local_id": 0,
            "website_id": 0,
            "parent_account_id": 0,
        },
    )
    result = MoveTransfer(MagicMock(), 100, 200).build_parameters(money)
    assert result["from_account_id"] == 200
    assert result["to_account_id"] == 999


def test_move_transfer_build_parameters_replaces_to_account_id() -> None:
    money = _make_money(
        mode="transfer",
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
        to_account=dict(FAKE_ACCOUNT),
    )
    result = MoveTransfer(MagicMock(), 100, 200).build_parameters(money)
    assert result["from_account_id"] == 999
    assert result["to_account_id"] == 200


def test_move_transfer_build_parameters_raises_when_from_account_is_none() -> None:
    money = _make_money(mode="transfer", from_account=None, to_account=dict(FAKE_ACCOUNT))
    with pytest.raises(ValueError, match="Missing account information for transfer"):
        MoveTransfer(MagicMock(), 100, 200).build_parameters(money)


def test_move_transfer_build_parameters_raises_when_to_account_is_none() -> None:
    money = _make_money(mode="transfer", from_account=dict(FAKE_ACCOUNT), to_account=None)
    with pytest.raises(ValueError, match="Missing account information for transfer"):
        MoveTransfer(MagicMock(), 100, 200).build_parameters(money)


def test_move_transfer_call_api_calls_update_transfer() -> None:
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
    assert result["from_account_id"] == 200


def test_move_payment_build_parameters_raises_when_from_account_is_none() -> None:
    money = _make_money(mode="payment", from_account=None)
    with pytest.raises(ValueError, match="Missing account information for payment"):
        MovePayment(MagicMock(), 100, 200).build_parameters(money)


def test_move_payment_call_api_calls_update_payment() -> None:
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
    assert result["to_account_id"] == 200


def test_move_income_build_parameters_raises_when_to_account_is_none() -> None:
    money = _make_money(mode="income", from_account=None, to_account=None)
    with pytest.raises(ValueError, match="Missing account information for income"):
        MoveIncome(MagicMock(), 100, 200).build_parameters(money)


def test_move_income_call_api_calls_update_income() -> None:
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
# Move.move (dispatcher)
# ---------------------------------------------------------------------------


def _make_move(fake_config: MagicMock, mock_api: MagicMock) -> Move:
    with (
        patch("zaimbackup.move.ZaimAPI", return_value=mock_api),
        patch("zaimbackup.move.Joiner"),
    ):
        return Move(fake_config, 100, 200)


def test_move_move_skips_when_neither_account_matches(fake_config: MagicMock) -> None:
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
    mock_api = MagicMock()
    move_obj = _make_move(fake_config, mock_api)
    money = _make_money(from_account=None, to_account=None)
    move_obj.move(money)
    mock_api.update_payment.assert_not_called()
    mock_api.update_transfer.assert_not_called()
    mock_api.update_income.assert_not_called()


def test_move_move_dispatches_payment(fake_config: MagicMock) -> None:
    mock_api = MagicMock()
    move_obj = _make_move(fake_config, mock_api)
    money = _make_money(mode="payment", from_account=dict(FAKE_ACCOUNT))
    move_obj.move(money)
    mock_api.update_payment.assert_called_once()
    mock_api.update_transfer.assert_not_called()
    mock_api.update_income.assert_not_called()


def test_move_move_dispatches_transfer(fake_config: MagicMock) -> None:
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
