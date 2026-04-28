"""Moves money entries from one account to another in Zaim."""

from logging import DEBUG
from logging import WARNING
from logging import basicConfig
from logging import getLogger

from zaimbackup.config import Config
from zaimbackup.move import Move

ACCOUNT_ID_MANUALLY_INPUT = 3
ACCOUNT_ID_API_CONNECTION = 20145626

basicConfig(level=DEBUG)
getLogger().setLevel(WARNING)


def main() -> None:
    Move(Config(), ACCOUNT_ID_MANUALLY_INPUT, ACCOUNT_ID_API_CONNECTION)()


if __name__ == "__main__":
    main()
