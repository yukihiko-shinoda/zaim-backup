"""Zaim API genre."""

from typing import TypedDict


class Genre(TypedDict):
    """Represents a genre in the Zaim API."""

    id: int
    category_id: int
    name: str
