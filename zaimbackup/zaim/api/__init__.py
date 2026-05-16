"""The package of Zaim API."""

from typing import cast

from pyzaim import ZaimAPI
from requests_oauthlib import OAuth1Session

from zaimbackup.zaim.api.models.account import Account
from zaimbackup.zaim.api.models.category import Category
from zaimbackup.zaim.api.models.genre import Genre


# Reason: pyzaim is not typed, so we need to cast the return type.
class ZaimApi(ZaimAPI):  # type: ignore[misc]
    """Zaim API client with typed return values and lazy OAuth initialisation."""

    verify_url = "https://api.zaim.net/v2/home/user/verify"
    money_url = "https://api.zaim.net/v2/home/money"
    payment_url = "https://api.zaim.net/v2/home/money/payment"
    income_url = "https://api.zaim.net/v2/home/money/income"
    transfer_url = "https://api.zaim.net/v2/home/money/transfer"
    category_url = "https://api.zaim.net/v2/home/category"
    genre_url = "https://api.zaim.net/v2/home/genre"
    account_url = "https://api.zaim.net/v2/home/account"
    currency_url = "https://api.zaim.net/v2/currency"
    callback_uri = "https://www.zaim.net/"

    # Reason: To override the constructor of ZaimAPI.
    def __init__(  # pylint: disable=super-init-not-called
        self,
        consumer_id: str,
        consumer_secret: str,
        access_token: str,
        access_token_secret: str,
        oauth_verifier: str,
    ) -> None:
        self.consumer_id = consumer_id
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.oauth_verifier = oauth_verifier
        self._auth: OAuth1Session | None = None

    @property
    def auth(self) -> OAuth1Session:
        """Return the OAuth1Session, initialising it on first access."""
        if self._auth:
            return self._auth
        self._auth = OAuth1Session(
            client_key=self.consumer_id,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
            callback_uri=self.callback_uri,
            verifier=self.oauth_verifier,
        )
        self._build_id_table()
        return self._auth

    def get_categories(self) -> list[Category]:
        return cast("list[Category]", self._get_category()["categories"])

    def get_genres(self) -> list[Genre]:
        return cast("list[Genre]", self._get_genre()["genres"])

    def get_accounts(self) -> list[Account]:
        return cast("list[Account]", self._get_account()["accounts"])
