"""Offline deterministic concurrency tests for GTI Reliability V2 candidate."""
import email.message
import importlib.util
import os
import threading
import time
import urllib.error
from pathlib import Path

os.environ.setdefault("NTFY_TOPIC", "gti-v2-offline-test-topic")

SOURCE = Path(__file__).with_name("btc_binance_signal_service.RELIABILITY_V2_CANDIDATE.py")
spec = importlib.util.spec_from_file_location("gti_v2_test_module", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def rate_limit_error(url, code=429, retry_after="120"):
    headers = email.message.Message()
    headers["Retry-After"] = retry_after
    return urllib.error.HTTPError(url, code, "rate limited", headers, None)


def test_binance_concurrent_call_is_suppressed():
    entered = threading.Event()
    release = threading.Event()
    second_started = threading.Event()
    calls = []
    outcomes = []
    mod.BINANCE_BLOCKED_UNTIL = 0.0
    mod.BINANCE_CONSECUTIVE_LIMITS = 0

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        entered.set()
        if not release.wait(3):
            raise AssertionError("test timed out waiting to release first Binance request")
        raise rate_limit_error(request.full_url)

    original = mod.urllib.request.urlopen
    mod.urllib.request.urlopen = fake_urlopen
    req = mod.urllib.request.Request("https://unit.test/binance")

    def first():
        try:
            mod._binance_urlopen(req, 1)
        except urllib.error.HTTPError:
            outcomes.append("first_http_429")

    def second():
        second_started.set()
        try:
            mod._binance_urlopen(req, 1)
            outcomes.append("second_unexpected_success")
        except mod.BinanceCooldownError:
            outcomes.append("second_suppressed")

    t1 = threading.Thread(target=first)
    t2 = threading.Thread(target=second)
    try:
        t1.start()
        assert entered.wait(2), "first Binance request did not enter fake transport"
        t2.start()
        assert second_started.wait(2), "second Binance caller did not start"
        time.sleep(0.05)
        release.set()
        t1.join(3)
        t2.join(3)
        assert not t1.is_alive() and not t2.is_alive(), "Binance threads did not finish"
        assert len(calls) == 1, f"expected one Binance HTTP request, got {len(calls)}"
        assert "first_http_429" in outcomes and "second_suppressed" in outcomes, outcomes
        print("PASS: concurrent Binance caller is serialized and suppressed after HTTP 429")
    finally:
        release.set()
        mod.urllib.request.urlopen = original
        mod.BINANCE_BLOCKED_UNTIL = 0.0


def test_ntfy_concurrent_call_is_suppressed():
    entered = threading.Event()
    release = threading.Event()
    second_started = threading.Event()
    calls = []
    outcomes = []
    mod.State.ntfy_blocked_until = 0.0
    mod.State.ntfy_consecutive_429 = 0
    mod.State.ntfy_delivery = {
        "successes": 0, "failures": 0, "rate_limited": 0, "deferred": 0,
        "cooldown_seconds": 0, "last_status": "never", "last_http_status": None,
        "last_error": None, "last_attempts": 0, "last_attempt_at": None,
        "last_success_at": None,
    }

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        entered.set()
        if not release.wait(3):
            raise AssertionError("test timed out waiting to release first ntfy request")
        raise rate_limit_error(request.full_url)

    original = mod.urllib.request.urlopen
    mod.urllib.request.urlopen = fake_urlopen

    def first():
        outcomes.append(("first", mod.send_ntfy("test", "first")))

    def second():
        second_started.set()
        outcomes.append(("second", mod.send_ntfy("test", "second")))

    t1 = threading.Thread(target=first)
    t2 = threading.Thread(target=second)
    try:
        t1.start()
        assert entered.wait(2), "first ntfy request did not enter fake transport"
        t2.start()
        assert second_started.wait(2), "second ntfy caller did not start"
        time.sleep(0.05)
        release.set()
        t1.join(3)
        t2.join(3)
        assert not t1.is_alive() and not t2.is_alive(), "ntfy threads did not finish"
        assert len(calls) == 1, f"expected one ntfy HTTP request, got {len(calls)}"
        assert ("first", False) in outcomes and ("second", False) in outcomes, outcomes
        assert mod.State.ntfy_delivery["rate_limited"] == 1
        assert mod.State.ntfy_delivery["deferred"] == 1
        print("PASS: concurrent ntfy caller waits, re-checks cooldown, and is deferred")
    finally:
        release.set()
        mod.urllib.request.urlopen = original
        mod.State.ntfy_blocked_until = 0.0


if __name__ == "__main__":
    test_binance_concurrent_call_is_suppressed()
    test_ntfy_concurrent_call_is_suppressed()
    print("ALL RELIABILITY V2 CONCURRENCY TESTS PASSED")
