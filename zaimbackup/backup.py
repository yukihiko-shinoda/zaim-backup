# SPDX-FileCopyrightText: Copyright (c) 2026 Yukihiko Shinoda
# SPDX-License-Identifier: MIT
"""Backup Zaim data to CSV."""

from __future__ import annotations

import csv
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from zaimbackup.config import Config
from zaimbackup.zaim.api import ZaimApi
from zaimbackup.zaim.api.models.money import MoneyTypeDef

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

    from zaimbackup.zaim.api.models.account import Account
    from zaimbackup.zaim.api.models.category import Category
    from zaimbackup.zaim.api.models.genre import Genre

# Kept outside the repository so that confidential data never shows up in Git or in the working tree,
# and so that the deny rule on ~/datasets in Claude Code's managed settings covers it:
# - Claude Codeに見せない技術: AIに入力できないデータを分析する
#   https://zenn.dev/green_tea/articles/a994964786cb4f
DIRECTORY_BACKUP = Path.home() / "datasets" / "zaim-backup"


def save_as_csv(file_path: Path, data: list[MoneyTypeDef]) -> None:
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=MoneyTypeDef.__annotations__.keys())
        writer.writeheader()
        writer.writerows(data)


def save_as_yaml(file_path: Path, data: Sequence[Category] | Sequence[Genre] | Sequence[Account]) -> None:
    rows: list[Mapping[str, object]] = list(data)
    file_path.write_text(yaml.safe_dump(rows, allow_unicode=True), encoding="utf-8")


def main(directory: Path = DIRECTORY_BACKUP) -> None:
    """Save money records and the master data needed to resolve their IDs into `directory`.

    The master data is saved because the money records hold only IDs of categories, genres, and accounts, and the Zaim
    API that resolves them will be discontinued on 2026-12-07.
    """
    api = ZaimApi(**Config().api)
    logger = getLogger(__name__)
    logger.debug(api.verify())
    directory.mkdir(parents=True, exist_ok=True)
    data: list[MoneyTypeDef] = api.get_data()
    save_as_csv(directory / "money.csv", data)
    save_as_yaml(directory / "categories.yml", api.get_categories())
    save_as_yaml(directory / "genres.yml", api.get_genres())
    save_as_yaml(directory / "accounts.yml", api.get_accounts())
