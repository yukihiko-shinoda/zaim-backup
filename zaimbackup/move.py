"""Moves money entries from one account to another in Zaim."""

from logging import DEBUG
from logging import getLogger
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import cast

from pyzaim import ZaimAPI
from requests import Response

from zaimbackup.config import Config
from zaimbackup.zaim.api.joiner import Joiner
from zaimbackup.zaim.api.models.money import Money
from zaimbackup.zaim.api.update import ParameterIncome
from zaimbackup.zaim.api.update import ParameterPayment
from zaimbackup.zaim.api.update import ParameterTransfer

TypeVarParameters = TypeVar("TypeVarParameters")


class AbstractMove(Generic[TypeVarParameters]):
    def __init__(self, zaim_api: ZaimAPI, account_to_be_replaced: int, account_to_replace_with: int) -> None:
        self.logger = getLogger(__name__)
        self.zaim_api = zaim_api
        self.account_to_be_replaced = account_to_be_replaced
        self.account_to_replace_with = account_to_replace_with

    def __call__(self, money: Money) -> None:
        parameters = self.build_parameters(money)
        self.logger.debug(parameters)
        self.call_api(parameters)

    def get_account_to_set(self, account_id: int) -> int:
        return self.account_to_replace_with if account_id == self.account_to_be_replaced else account_id

    def build_parameters(self, money: Money) -> TypeVarParameters:
        raise NotImplementedError

    def call_api(self, parameters: TypeVarParameters) -> Response:
        raise NotImplementedError


class MoveTransfer(AbstractMove[ParameterTransfer]):
    def __init__(self, zaim_api: ZaimAPI, account_to_be_replaced: int, account_to_replace_with: int) -> None:
        super().__init__(zaim_api, account_to_be_replaced, account_to_replace_with)
        self.logger.setLevel(DEBUG)

    def build_parameters(self, money: Money) -> ParameterTransfer:
        if not money.from_account or not money.to_account:
            msg = f"Missing account information for transfer: {money}"
            raise ValueError(msg)
        self.logger.debug(
            "%s %s %s -> %s",
            money.date,
            money.mode,
            money.from_account["name"],
            money.to_account["name"],
        )
        return {
            "data_id": money.id,
            "date": money.date_as_date,
            "amount": money.amount,
            "from_account_id": self.get_account_to_set(money.from_account["id"]),
            "to_account_id": self.get_account_to_set(money.to_account["id"]),
            "comment": money.comment,
        }

    def call_api(self, parameters: ParameterTransfer) -> Response:
        return cast("Response", self.zaim_api.update_transfer(**parameters))


class MovePayment(AbstractMove[ParameterPayment]):
    def build_parameters(self, money: Money) -> ParameterPayment:
        if not money.from_account:
            msg = f"Missing account information for payment: {money}"
            raise ValueError(msg)
        self.logger.debug("%s %s %s", money.date, money.mode, money.from_account["name"])
        return {
            "data_id": money.id,
            "date": money.date_as_date,
            "amount": money.amount,
            "category_id": money.category["id"] if money.category else None,
            "genre_id": money.genre["id"] if money.genre else None,
            "from_account_id": self.get_account_to_set(money.from_account["id"]),
            "comment": money.comment,
            "name": money.name,
            "place": money.place,
        }

    def call_api(self, parameters: ParameterPayment) -> Response:
        return cast("Response", self.zaim_api.update_payment(**parameters))


class MoveIncome(AbstractMove[ParameterIncome]):
    def build_parameters(self, money: Money) -> ParameterIncome:
        if not money.to_account:
            msg = f"Missing account information for income: {money}"
            raise ValueError(msg)
        self.logger.debug("%s %s %s", money.date, money.mode, money.to_account["name"])
        return {
            "data_id": money.id,
            "date": money.date_as_date,
            "category_id": money.category["id"] if money.category else None,
            "amount": money.amount,
            "to_account_id": self.get_account_to_set(money.to_account["id"]),
            "comment": money.comment,
            "place": money.place,
        }

    def call_api(self, parameters: ParameterIncome) -> Response:
        return cast("Response", self.zaim_api.update_income(**parameters))


class Move:
    def __init__(self, config: Config, account_to_be_replaced: int, account_to_replace_with: int) -> None:
        self.join = Joiner(config)
        self.account_to_be_replaced = account_to_be_replaced
        self.account_to_replace_with = account_to_replace_with
        zaim_api = ZaimAPI(**config.api)
        self.dictionary_move_process: dict[str, AbstractMove[Any]] = {
            "transfer": MoveTransfer(zaim_api, self.account_to_be_replaced, self.account_to_replace_with),
            "payment": MovePayment(zaim_api, self.account_to_be_replaced, self.account_to_replace_with),
            "income": MoveIncome(zaim_api, self.account_to_be_replaced, self.account_to_replace_with),
        }

    def __call__(self) -> None:
        for money in self.join.list_money:
            self.move(money)

    def move(self, money: Money) -> None:
        # if not (money.date_as_date.year >= 2025 and money.date_as_date.month >= 3):
        #     return
        if (not money.from_account or money.from_account["id"] != self.account_to_be_replaced) and (
            not money.to_account or money.to_account["id"] != self.account_to_be_replaced
        ):
            return
        self.dictionary_move_process[money.mode](money)
