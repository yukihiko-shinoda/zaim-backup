"""To join Zaim API data into Money objects."""

import copy
from collections.abc import Generator
from collections.abc import Iterable
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import cast

from zaimbackup.config import Config
from zaimbackup.zaim.api.cache import ZaimCache
from zaimbackup.zaim.api.models.money import Money
from zaimbackup.zaim.api.models.money import MoneyTypeDef

if TYPE_CHECKING:
    from typing import Any

TypeVarMoney = TypeVar("TypeVarMoney", bound=Money)


class Joiner:
    """Enriches raw MoneyTypeDef records with joined Category, Genre, and Account objects."""

    def __init__(self, config: Config, *, model_money: type[Money] | None = None) -> None:
        self.zaim_cache = ZaimCache(config)
        self.dict_category = {category["id"]: category for category in self.zaim_cache.categories}
        self.dict_genre = {genre["id"]: genre for genre in self.zaim_cache.genres}
        self.dict_account = {account["id"]: account for account in self.zaim_cache.accounts}
        self.model_money: type[Money] = model_money or Money
        self._list_money_object: Generator[Money] | None = None

    @property
    def list_money(self) -> Generator[Money]:
        if self._list_money_object is None:
            self._list_money_object = self.join(self.zaim_cache.money)
        return self._list_money_object

    def join(self, list_money: Iterable[MoneyTypeDef]) -> Generator[Money]:
        return (self.create_money_object(money) for money in list_money)

    def create_money_object(self, money: MoneyTypeDef) -> Money:
        """Create a money object from a MoneyTypeDef."""
        copied = cast("dict[str, Any]", copy.deepcopy(money))
        category_id = money["category_id"]
        copied["category"] = self.dict_category[category_id] if category_id else None
        genre_id = money["genre_id"]
        copied["genre"] = self.dict_genre[genre_id] if genre_id else None
        from_account_id = money["from_account_id"]
        copied["from_account"] = self.dict_account[from_account_id] if from_account_id else None
        to_account_id = money["to_account_id"]
        copied["to_account"] = self.dict_account[to_account_id] if to_account_id else None
        return self.model_money(**copied)
