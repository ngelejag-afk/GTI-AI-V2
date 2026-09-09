from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request


class MT5BridgeClient:

    @staticmethod
    def url() -> str:
        return (
            os.getenv("GTI_BRIDGE_URL", "")
            .strip()
            .rstrip("/")
        )

    @staticmethod
    def secret() -> str:
        return os.getenv(
            "GTI_BRIDGE_SECRET",
            "",
        ).strip()

    @classmethod
    def _headers(cls) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "GTI-AI-V2/1.0",
        }

        secret = cls.secret()

        if secret:
            headers["Authorization"] = (
                f"Bearer {secret}"
            )

        return headers

    @classmethod
    def get_snapshot(
        cls,
        symbol: str = "XAUUSD",
    ) -> dict:

        base = cls.url()

        if not base:
            return {
                "ok": False,
                "error": "GTI_BRIDGE_URL_NOT_CONFIGURED",
            }

        query = urllib.parse.urlencode(
            {"symbol": symbol}
        )

        url = f"{base}/snapshot?{query}"

        try:
            request = urllib.request.Request(
                url,
                headers=cls._headers(),
                method="GET",
            )

            with urllib.request.urlopen(
                request,
                timeout=10,
            ) as response:

                raw = response.read().decode(
                    "utf-8"
                )

                data = json.loads(raw)

            if not isinstance(data, dict):
                return {
                    "ok": False,
                    "error": "INVALID_BRIDGE_RESPONSE",
                }

            data["ok"] = True

            return data

        except urllib.error.HTTPError as exc:
            return {
                "ok": False,
                "error": f"BRIDGE_HTTP_{exc.code}",
            }

        except urllib.error.URLError as exc:
            return {
                "ok": False,
                "error": (
                    "BRIDGE_CONNECTION_ERROR:"
                    f"{exc.reason}"
                ),
            }

        except json.JSONDecodeError:
            return {
                "ok": False,
                "error": "INVALID_JSON_FROM_BRIDGE",
            }

        except Exception as exc:
            return {
                "ok": False,
                "error": (
                    "BRIDGE_ERROR:"
                    f"{type(exc).__name__}"
                ),
            }


class BridgeMarketData:

    @classmethod
    def candles(
        cls,
        symbol: str,
        timeframe: str,
        count: int = 200,
    ) -> list:

        snapshot = MT5BridgeClient.get_snapshot(
            symbol
        )

        if not snapshot.get("ok"):
            return []

        market = snapshot.get(
            "market",
            {},
        )

        rows = market.get(
            timeframe,
            [],
        )

        if not isinstance(rows, list):
            return []

        return rows[-count:]

    @classmethod
    def price(
        cls,
        symbol: str,
    ) -> dict:

        snapshot = MT5BridgeClient.get_snapshot(
            symbol
        )

        if not snapshot.get("ok"):
            return {}

        price = snapshot.get(
            "price",
            {},
        )

        if not isinstance(price, dict):
            return {}

        return price
