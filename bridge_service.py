from __future__ import annotations

import os
import threading
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query

app = FastAPI(
    title="GTI-AI-V2 Read-Only MT5 Bridge",
    version="1.0.0",
)

_STORE: dict[str, dict[str, Any]] = {}
_LOCK = threading.Lock()


def _secret() -> str:
    return os.getenv("GTI_BRIDGE_SECRET", "").strip()


def _max_age() -> int:
    try:
        return max(5, int(os.getenv("GTI_BRIDGE_MAX_AGE", "120")))
    except ValueError:
        return 120


def _auth(authorization: str | None) -> None:
    secret = _secret()

    if not secret:
        raise HTTPException(
            status_code=503,
            detail="BRIDGE_SECRET_NOT_CONFIGURED",
        )

    if authorization != f"Bearer {secret}":
        raise HTTPException(
            status_code=401,
            detail="UNAUTHORIZED",
        )


def _validate_snapshot(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400,
            detail="INVALID_JSON_OBJECT",
        )

    symbol = str(payload.get("symbol", "")).strip()

    if not symbol:
        raise HTTPException(
            status_code=400,
            detail="SYMBOL_REQUIRED",
        )

    market = payload.get("market")
    price = payload.get("price")

    if not isinstance(market, dict):
        raise HTTPException(
            status_code=400,
            detail="MARKET_REQUIRED",
        )

    if not isinstance(price, dict):
        raise HTTPException(
            status_code=400,
            detail="PRICE_REQUIRED",
        )

    required_timeframes = (
        "H4",
        "H1",
        "M15",
        "M5",
        "M1",
    )

    for timeframe in required_timeframes:
        rows = market.get(timeframe)

        if not isinstance(rows, list):
            raise HTTPException(
                status_code=400,
                detail=f"INVALID_TIMEFRAME:{timeframe}",
            )

    try:
        bid = float(price["bid"])
        ask = float(price["ask"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="INVALID_PRICE",
        )

    if bid <= 0 or ask <= 0:
        raise HTTPException(
            status_code=400,
            detail="INVALID_PRICE_VALUE",
        )

    if ask < bid:
        raise HTTPException(
            status_code=400,
            detail="INVALID_SPREAD",
        )

    now = int(time.time())

    source_time = payload.get("received_at", now)

    try:
        source_time = int(source_time)
    except (TypeError, ValueError):
        source_time = now

    cleaned = dict(payload)

    cleaned["symbol"] = symbol
    cleaned["received_at"] = now
    cleaned["source_time"] = source_time

    return cleaned


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "GTI-AI-V2 MT5 Bridge",
        "status": "OK",
        "mode": "READ_ONLY",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    with _LOCK:
        symbols = list(_STORE.keys())

    return {
        "status": "OK",
        "symbols": symbols,
        "read_only": True,
    }


@app.post("/ingest")
def ingest(
    payload: dict[str, Any],
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:

    _auth(authorization)

    snapshot = _validate_snapshot(payload)
    symbol = snapshot["symbol"]

    with _LOCK:
        _STORE[symbol] = snapshot

    return {
        "ok": True,
        "symbol": symbol,
        "received_at": snapshot["received_at"],
        "candles": {
            timeframe: len(snapshot["market"][timeframe])
            for timeframe in ("H4", "H1", "M15", "M5", "M1")
        },
    }


@app.get("/snapshot")
def snapshot(
    symbol: str = Query(default="XAUUSD"),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:

    _auth(authorization)

    symbol = symbol.strip()

    with _LOCK:
        data = _STORE.get(symbol)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="SNAPSHOT_NOT_AVAILABLE",
        )

    age = int(time.time()) - int(
        data.get("received_at", 0)
    )

    if age > _max_age():
        raise HTTPException(
            status_code=409,
            detail="STALE_SNAPSHOT",
        )

    return data


# IMPORTANT:
# This service intentionally has NO order/trading endpoint.
# It is a READ-ONLY market-data bridge.
