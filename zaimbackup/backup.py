"""Backup Zaim data to CSV."""

import csv
from logging import getLogger
from pathlib import Path

from pyzaim import ZaimAPI

from zaimbackup.config import Config
from zaimbackup.zaim.api.models.money import MoneyTypeDef


def save_as_csv(file_path: Path, data: list[MoneyTypeDef]) -> None:
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=MoneyTypeDef.__annotations__.keys())
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    api = ZaimAPI(**Config().api)
    logger = getLogger(__name__)
    logger.debug(api.verify())
    data: list[MoneyTypeDef] = api.get_data()
    save_as_csv(Path("money.csv"), data)
