"""To cache Zaim API data."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict
from typing import TypeVar
from typing import cast
from typing import get_type_hints

import yaml

from zaimbackup.zaim.api import ZaimApi
from zaimbackup.zaim.api.models.money import MoneyTypeDef

if TYPE_CHECKING:
    from collections.abc import Generator

    from zaimbackup.config import Config
    from zaimbackup.zaim.api.models.category import Category
    from zaimbackup.zaim.api.models.genre import Genre

TypeVarTypedDict = TypeVar("TypeVarTypedDict")


class TypedDictReference(TypedDict):
    pass


TypedDictMeta = TypedDictReference().__class__.__bases__[0]


class TypeFix[TypeVarTypedDict]:
    """Applies TypedDict field types to a raw string-keyed dict row."""

    def __init__(self, type_typed_dict: type[TypeVarTypedDict]) -> None:
        if not isinstance(type_typed_dict, type) or not issubclass(type_typed_dict, TypedDictMeta):
            msg = f"Expected a subclass of TypedDict, got {type_typed_dict}"
            raise TypeError(msg)
        self.type_typed_dict = type_typed_dict

    def __call__(self, row: dict[str, Any]) -> TypeVarTypedDict:
        type_hints = get_type_hints(self.type_typed_dict)
        return cast("TypeVarTypedDict", {key: type_hints[key](value) for key, value in row.items()})


class ZaimCache:
    """Caches Zaim API responses to local CSV and YAML files."""

    DIRECTORY_CACHE = Path(".cache_zaim_api")
    DUMP_MONEY = DIRECTORY_CACHE / "zaim_money.csv"
    DUMP_CATEGORIES = DIRECTORY_CACHE / "zaim_categories.yml"
    DUMP_GENRES = DIRECTORY_CACHE / "zaim_genres.yml"
    DUMP_ACCOUNTS = DIRECTORY_CACHE / "zaim_accounts.yml"

    def __init__(self, config: Config) -> None:
        self.zaim_api = ZaimApi(**config.api)

    def dump_to_yaml(self, dictionary: list[dict[str, Any]], file: Path) -> None:
        file.write_text(yaml.safe_dump(dictionary, allow_unicode=True))

    # Reason: YAML is not typed.
    def load_from_yaml(self, file: Path) -> Any:  # noqa: ANN401
        return yaml.safe_load(file.read_text())

    def dump_to_csv(self, header: list[str], dictionary: list[dict[str, Any]], file: Path) -> None:
        with file.open("w", encoding="utf-8") as text_io:
            writer = csv.DictWriter(text_io, fieldnames=header)
            writer.writerows(dictionary)

    def load_from_csv(
        self,
        header: list[str],
        file: Path,
        typed_dict: type[TypeVarTypedDict],
    ) -> Generator[TypeVarTypedDict]:
        """Yield typed rows from a CSV file, converting each value to its TypedDict field type."""
        type_fix = TypeFix(typed_dict)
        with file.open("r", encoding="utf-8") as text_io:
            yield from (type_fix(row) for row in csv.DictReader(text_io, fieldnames=header))

    def fix_type(self, row: dict[str, Any], typed_dict: type[TypeVarTypedDict]) -> TypeVarTypedDict:
        type_hints = get_type_hints(typed_dict)
        return cast("TypeVarTypedDict", {key: type_hints[key](value) for key, value in row.items()})

    @property
    def money(self) -> Generator[MoneyTypeDef]:
        """Return money rows, fetching from the API and caching to CSV on the first call."""
        property_names = list(get_type_hints(MoneyTypeDef).keys())
        if not self.DUMP_MONEY.exists():
            self.dump_to_csv(property_names, self.zaim_api.get_data(), self.DUMP_MONEY)
        # Reason: YAML is not typed.
        return self.load_from_csv(property_names, self.DUMP_MONEY, MoneyTypeDef)

    @property
    def categories(self) -> list[Category]:
        """Return categories, fetching from the API and caching to YAML on the first call."""
        if not self.DUMP_CATEGORIES.exists():
            # Reason: The mypy's issue:
            # - TypedDict cannot be used where a normal dict is expected · Issue #4976 · python/mypy · GitHub
            #   https://github.com/python/mypy/issues/4976
            self.dump_to_yaml(self.zaim_api.get_categories(), self.DUMP_CATEGORIES)  # type: ignore[arg-type]
        # Reason: YAML is not typed.
        return self.load_from_yaml(self.DUMP_CATEGORIES)  # type: ignore[no-any-return]

    @property
    def genres(self) -> list[Genre]:
        """Return genres, fetching from the API and caching to YAML on the first call."""
        if not self.DUMP_GENRES.exists():
            # Reason: The mypy's issue:
            # - TypedDict cannot be used where a normal dict is expected · Issue #4976 · python/mypy · GitHub
            #   https://github.com/python/mypy/issues/4976
            self.dump_to_yaml(self.zaim_api.get_genres(), self.DUMP_GENRES)  # type: ignore[arg-type]
        # Reason: YAML is not typed.
        return self.load_from_yaml(self.DUMP_GENRES)  # type: ignore[no-any-return]

    @property
    def accounts(self) -> list[Genre]:
        """Return accounts, fetching from the API and caching to YAML on the first call."""
        if not self.DUMP_ACCOUNTS.exists():
            # Reason: The mypy's issue:
            # - TypedDict cannot be used where a normal dict is expected · Issue #4976 · python/mypy · GitHub
            #   https://github.com/python/mypy/issues/4976
            self.dump_to_yaml(self.zaim_api.get_accounts(), self.DUMP_ACCOUNTS)  # type: ignore[arg-type]
        # Reason: YAML is not typed.
        return self.load_from_yaml(self.DUMP_ACCOUNTS)  # type: ignore[no-any-return]
