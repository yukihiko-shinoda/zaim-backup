"""Config module for Zaim API."""

from pathlib import Path
from typing import Any

from yaml import safe_load


# Reason: Actually dataclass. pylint: disable-next=too-few-public-methods
class Config:
    def __init__(self) -> None:
        config: dict[str, Any] = safe_load(Path("config.yml").read_text(encoding="utf-8"))
        self.api = config["api"]
        self.account_id_manually_input = config.get("account_id_manually_input")
        self.account_id_api_connection = config.get("account_id_api_connection")
