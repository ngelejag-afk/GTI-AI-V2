from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone

import json
import os
import time

from market_data.twelvedata_xau import TwelveDataXAU
from market_data.dxy_cache import DXYCache
from news.forex_factory_calendar import check as check_news
from strategy.institutional_entry_engine import InstitutionalEntryEngine
from utils.notifier import send_ntfy_signal

SYMBOL = os.getenv("GTI_SYMBOL", "XAU/USD").strip() or "XAU/USD"

TIMEFRAMES = ("H4", "H1", "M5", "M1")
STATE_FILE = "runtime_cache/live_signal_state.json"


def _signal_key(result: dict) -> str:
    return "|".join(
        str(result.get(name))
        for name in ("bias", "entry", "sl", "tp1", "tp2")
    )


def _load_signal_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        if isinstance(state, dict):
            return state
    except (OSError, ValueError, TypeError):
        pass
    return {
        "last_signal_key": None,
        "last_signal_time": None,
        "active_signal": None,
    }


def _save_signal_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, separators=(",", ":"))




def _xau_weekend_closed() -> bool:
    symbol = SYMBOL.upper().replace(" ", "")
    return symbol in {"XAU/USD", "XAUUSD"} and datetime.now(timezone.utc).weekday() >= 5


def _read_api_key() -> str:
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("TWELVE_DATA_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")


def _ema(values: list[float], period: int) -> float:
    if len(values) < period:
        raise RuntimeError(f"INSUFFICIENT_DXY_EMA_DATA:{len(values)}")

    multiplier = 2 / (period + 1)
    value = sum(values[:period]) / period

    for item in values[period:]:
        value = (item - value) * multiplier + value

    return value


def _get_dxy_signal() -> tuple[str, float, float, float, float]:
    key = _read_api_key()
    dxy = DXYCache.load_or_build(key, count=200)

    ema20 = _ema(dxy, 20)
    ema50 = _ema(dxy, 50)
    ema200 = _ema(dxy, 200)

    if ema20 > ema50 > ema200:
        signal = "USD_STRENGTH"
    elif ema20 < ema50 < ema200:
        signal = "USD_WEAKNESS"
    else:
        signal = "NEUTRAL"

    return signal, dxy[-1], ema20, ema50, ema200


def main() -> None:
    print("GTI-AI-V2 INSTITUTIONAL SCANNER")
    print("Mode: READ-ONLY")
    print("Trading: DISABLED")
    print("Provider: Twelve Data")
    print(f"Symbol: {SYMBOL}")
    if _xau_weekend_closed():
        print(json.dumps({
            "status": "NO TRADE",
            "reason": "XAUUSD_WEEKEND_CLOSED",
            "symbol": SYMBOL,
            "utc_day": datetime.now(timezone.utc).strftime("%A"),
        }, indent=2))
        return


    try:
        quote = TwelveDataXAU.get_quote()
    except Exception as exc:
        print(json.dumps({
            "status": "NO TRADE",
            "reason": "TWELVE_DATA_QUOTE_ERROR",
            "symbol": SYMBOL,
            "error": f"{type(exc).__name__}: {exc}",
        }, indent=2))
        return

    age = int(quote["age_seconds"])

    if age > 120:
        print(json.dumps({
            "status": "NO TRADE",
            "reason": "STALE_MARKET_QUOTE",
            "symbol": SYMBOL,
            "quote_age_seconds": age,
        }, indent=2))
        return

    if not quote["market_open"]:
        print(json.dumps({
            "status": "NO TRADE",
            "reason": "MARKET_CLOSED",
            "symbol": SYMBOL,
            "price": quote["price"],
            "last_quote_utc": quote["last_quote_utc"],
        }, indent=2))
        return

    try:
        dxy_signal, dxy_value, dxy_ema20, dxy_ema50, dxy_ema200 = _get_dxy_signal()
    except Exception as exc:
        print(json.dumps({
            "status": "NO TRADE",
            "reason": "SYNTHETIC_DXY_ERROR",
            "symbol": SYMBOL,
            "error": f"{type(exc).__name__}: {exc}",
        }, indent=2))
        return

    news = check_news()

    if not news.get("available") or not news.get("safe"):
        print(json.dumps({
            "status": "NO TRADE",
            "reason": news.get("reason", "NEWS_GATE_BLOCKED"),
            "symbol": SYMBOL,
            "news_safe": False,
            "news_risk": news.get("risk"),
            "blocking_event": news.get("blocking_event"),
            "events_checked": news.get("events_checked"),
            "news_error": news.get("error"),
        }, indent=2, default=str))
        return

    market = {}
    cache_dir = Path("runtime_cache/xau_candles")
    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        for timeframe in TIMEFRAMES:
            cache_file = cache_dir / f"{SYMBOL.replace(chr(47), chr(95))}_{timeframe}.json"
            cached = None
            if cache_file.exists():
                try:
                    cached = json.loads(cache_file.read_text(encoding="utf-8")).get("candles")
                except (OSError, ValueError, TypeError):
                    cached = None
            cache_ttl = {"H4": 14400, "H1": 3600, "M5": 300, "M1": 60}[timeframe]
            cache_age = time.time() - cache_file.stat().st_mtime if cache_file.exists() else float("inf")
            if isinstance(cached, list) and len(cached) >= 80 and cache_age < cache_ttl:
                market[timeframe] = cached[-80:]
                print(f"CANDLE CACHE HIT: {timeframe} age={int(cache_age)}s bars={len(market[timeframe])}")
            else:
                candles = TwelveDataXAU.get_candles(timeframe, count=80)
                market[timeframe] = candles
                cache_file.write_text(json.dumps({"candles": candles}, separators=(chr(44), chr(58))), encoding="utf-8")
                print(f"CANDLE CACHE WRITE: {timeframe} bars={len(candles)}")
    except Exception as exc:
        print(json.dumps({
            "status": "NO TRADE",
            "reason": "TWELVE_DATA_CANDLE_ERROR",
            "symbol": SYMBOL,
            "error": f"{type(exc).__name__}: {exc}",
        }, indent=2))
        return

    price = float(quote["price"])

    result = InstitutionalEntryEngine.scan(
        market,
        bid=price,
        ask=price,
        dxy_signal=dxy_signal,
        news_safe=True,
    )

    result["symbol"] = SYMBOL
    result["provider"] = "Twelve Data"
    result["news_safe"] = True
    result["news_reason"] = news.get("reason")
    result["events_checked"] = news.get("events_checked")
    result["dxy_signal"] = dxy_signal
    result["dxy_value"] = dxy_value
    result["dxy_ema20"] = dxy_ema20
    result["dxy_ema50"] = dxy_ema50
    result["dxy_ema200"] = dxy_ema200
    result["quote_price"] = price
    result["quote_age_seconds"] = age
    result["last_quote_utc"] = quote["last_quote_utc"]
    result["market_open"] = quote["market_open"]

    # Notify only when the institutional engine confirms the entry zone is active.
    # Duplicate protection prevents repeated alerts for the same setup.
    if result.get("status") == "ENTER NOW":
        state = _load_signal_state()
        key = _signal_key(result)

        if state.get("last_signal_key") != key:
            action = "BUY" if result.get("bias") == "BUY" else "SELL"
            send_ntfy_signal(
                symbol=SYMBOL,
                action=action,
                entry=result.get("entry"),
                sl=result.get("sl"),
                tp1=result.get("tp1"),
                tp2=result.get("tp2"),
                tf="M1",
                rr=result.get("rr"),
                confidence=result.get("confidence"),
                bias=result.get("bias"),
                invalidation=result.get("invalidation"),
            )

            state["last_signal_key"] = key
            state["last_signal_time"] = int(time.time())
            state["active_signal"] = {
                "action": action,
                "entry": result.get("entry"),
                "sl": result.get("sl"),
                "tp1": result.get("tp1"),
                "tp2": result.get("tp2"),
            }
            _save_signal_state(state)
            print("SIGNAL DISPATCH: NEW")
        else:
            print("SIGNAL DISPATCH: DUPLICATE BLOCKED")

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
