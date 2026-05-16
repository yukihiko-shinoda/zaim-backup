"""To issue access token for Zaim API.

- liebe-magi/pyzaim: Zaimのデータを取得・操作するPythonパッケージ
  https://github.com/liebe-magi/pyzaim
"""

# Reason: Only importing library function
from pyzaim import get_access_token  # pragma: no cover

# Reason: Only calling library function
if __name__ == "__main__":  # pragma: no cover
    get_access_token()
