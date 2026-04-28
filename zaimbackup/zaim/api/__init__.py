"""The package of Zaim API."""

from typing import cast

from pyzaim import ZaimAPI
from requests_oauthlib import OAuth1Session

from zaimbackup.zaim.api.models.account import Account
from zaimbackup.zaim.api.models.category import Category
from zaimbackup.zaim.api.models.genre import Genre


# Reason: pyzaim is not typed, so we need to cast the return type.
class ZaimApi(ZaimAPI):  # type: ignore[misc]
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

        self.verify_url = "https://api.zaim.net/v2/home/user/verify"
        self.money_url = "https://api.zaim.net/v2/home/money"
        self.payment_url = "https://api.zaim.net/v2/home/money/payment"
        self.income_url = "https://api.zaim.net/v2/home/money/income"
        self.transfer_url = "https://api.zaim.net/v2/home/money/transfer"
        self.category_url = "https://api.zaim.net/v2/home/category"
        self.genre_url = "https://api.zaim.net/v2/home/genre"
        self.account_url = "https://api.zaim.net/v2/home/account"
        self.currency_url = "https://api.zaim.net/v2/currency"
        self.callback_uri = "https://www.zaim.net/"

        self._auth: OAuth1Session | None = None

    @property
    def auth(self) -> OAuth1Session:
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
