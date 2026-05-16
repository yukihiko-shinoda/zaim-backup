"""Tests for ZaimApi."""

from unittest.mock import patch

from zaimbackup.zaim.api import ZaimApi

FAKE_CATEGORY = {"id": 1, "name": "食費", "mode": "payment"}
FAKE_GENRE = {"id": 10, "category_id": 1, "name": "外食"}
FAKE_ACCOUNT = {"id": 100, "name": "現金", "active": 1}


def _make_api() -> ZaimApi:
    return ZaimApi("fake", "fake", "fake", "fake", "fake")


def test_auth_creates_oauth_session_with_correct_credentials() -> None:
    """Auth property constructs an OAuth1Session with the credentials supplied to __init__."""
    api = _make_api()
    with patch("zaimbackup.zaim.api.OAuth1Session") as mock_session_cls, patch.object(api, "_build_id_table"):
        result = api.auth
        mock_session_cls.assert_called_once_with(
            client_key="fake",
            client_secret="fake",  # nosec: B106 # noqa: S106 -- fake credentials
            resource_owner_key="fake",
            resource_owner_secret="fake",  # nosec: B106 # noqa: S106 -- fake credentials
            callback_uri="https://www.zaim.net/",
            verifier="fake",
        )
        assert result is mock_session_cls.return_value


def test_auth_is_cached_and_calls_build_id_table_once() -> None:
    """Auth is memoised: OAuth1Session and _build_id_table are each called exactly once."""
    api = _make_api()
    with (
        patch("zaimbackup.zaim.api.OAuth1Session") as mock_session_cls,
        patch.object(api, "_build_id_table") as mock_build,
    ):
        first = api.auth
        second = api.auth
        assert first is second
        assert mock_session_cls.call_count == 1
        assert mock_build.call_count == 1


def test_get_categories_returns_categories_list() -> None:
    api = _make_api()
    with patch.object(api, "_get_category", return_value={"categories": [FAKE_CATEGORY]}):
        assert api.get_categories() == [FAKE_CATEGORY]


def test_get_genres_returns_genres_list() -> None:
    api = _make_api()
    with patch.object(api, "_get_genre", return_value={"genres": [FAKE_GENRE]}):
        assert api.get_genres() == [FAKE_GENRE]


def test_get_accounts_returns_accounts_list() -> None:
    api = _make_api()
    with patch.object(api, "_get_account", return_value={"accounts": [FAKE_ACCOUNT]}):
        assert api.get_accounts() == [FAKE_ACCOUNT]
