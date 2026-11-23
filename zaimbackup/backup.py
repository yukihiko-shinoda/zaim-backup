# SPDX-FileCopyrightText: Copyright (c) 2026 Yukihiko Shinoda
# SPDX-License-Identifier: MIT
"""Backup Zaim data to CSV."""

import csv
from logging import getLogger
from pathlib import Path

from pyzaim import ZaimAPI

from zaimbackup.config import Config
from zaimbackup.zaim.api.models.money import MoneyTypeDef

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


def main(directory: Path = DIRECTORY_BACKUP) -> None:
    api = ZaimAPI(**Config().api)
    logger = getLogger(__name__)
    logger.debug(api.verify())
    directory.mkdir(parents=True, exist_ok=True)
    data: list[MoneyTypeDef] = api.get_data()
    save_as_csv(directory / "money.csv", data)
