"""Tests for zaimbackup/backup.py: save_as_csv and main."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

from zaimbackup.backup import main
from zaimbackup.backup import save_as_csv
from zaimbackup.zaim.api.models.money import MoneyTypeDef

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_save_as_csv_writes_header_and_row(tmp_path: Path, mock_zaim_api: MagicMock) -> None:
    """save_as_csv writes a header row and the provided data rows to the output file."""
    out = tmp_path / "out.csv"
    data = mock_zaim_api.get_data.return_value
    save_as_csv(out, data)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert list(MoneyTypeDef.__annotations__.keys()) == list(rows[0].keys())
    assert rows[0]["amount"] == "500"
    assert rows[0]["date"] == "2024-01-15"


def test_save_as_csv_empty_data(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    save_as_csv(out, [])
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert lines[0] == ",".join(MoneyTypeDef.__annotations__.keys())


def test_main_creates_money_csv(
    fake_config: MagicMock,
    mock_zaim_api: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Main() calls the Zaim API and writes money.csv to the current directory."""
    monkeypatch.chdir(tmp_path)
    with (
        patch("zaimbackup.backup.ZaimAPI", return_value=mock_zaim_api) as mock_cls,
        patch("zaimbackup.backup.Config", return_value=fake_config),
    ):
        main()
    mock_cls.assert_called_once_with(**fake_config.api)
    mock_zaim_api.get_data.assert_called_once()
    assert (tmp_path / "money.csv").exists()
