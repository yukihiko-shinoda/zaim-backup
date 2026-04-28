"""Zaim API category."""

from typing import TypedDict


class Category(TypedDict):
    """Represents a category in the Zaim API."""

    id: int
    name: str
    mode: str
    sort: int
    parent_category_id: int
    active: int
    modified: str
