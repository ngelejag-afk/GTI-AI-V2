



from pathlib import Path

import pytest

from gti_v2_unified_daemon import (
    Direction,
    Indicators,
    SignalState,
    SignalStateMachine,
    StrategySignal,
)


@pytest.fixture
def temp_state_file(tmp_path: Path) -> Path:
    return tmp_path / "test_signal_state.json"


def make_buy_signal(
    entry: float = 2350.0,
    stop: float = 2345.0,
    target: float = 2360.0,
    timestamp: float = 1000.0,
) -> StrategySignal:
    return StrategySignal(
        direction=Direction.BUY,
        entry=entry,
        stop=stop,
        target=target,
        risk_reward=2.0,
        score=0.90,
        valid=True,
        reason="Test bullish signal",
        candle_timestamp=timestamp,
        indicators=Indicators(
            ema_fast=2352.0,
            ema_slow=2340.0,
            rsi=55.0,
            atr=2.0,
            volume_sma=100.0,
        ),
    )


def make_sell_signal() -> StrategySignal:
    return StrategySignal(
        direction=Direction.SELL,
        entry=2355.0,
        stop=2360.0,
        target=2345.0,
        risk_reward=2.0,
        score=0.90,
        valid=True,
        reason="Sell flip",
        candle_timestamp=1005.0,
        indicators=Indicators(
            ema_fast=2340.0,
            ema_slow=2355.0,
            rsi=45.0,
            atr=2.0,
            volume_sma=100.0,
        ),
    )


def test_state_machine_initial_state(
    temp_state_file: Path,
) -> None:
    sm = SignalStateMachine(filepath=temp_state_file)

    assert sm.state == SignalState.WAIT


def test_duplicate_suppression(
    temp_state_file: Path,
) -> None:
    sm = SignalStateMachine(filepath=temp_state_file)
    signal = make_buy_signal()

    sm.transition_alert(signal)

    assert sm.state == SignalState.ALERT_SENT

    should_alert, reason = sm.should_alert(signal)

    assert not should_alert
    assert "Duplicate signal" in reason


def test_direction_flip_permits_alert(
    temp_state_file: Path,
) -> None:
    sm = SignalStateMachine(filepath=temp_state_file)

    signal1 = make_buy_signal()
    sm.transition_alert(signal1)

    signal2 = make_sell_signal()

    should_alert, reason = sm.should_alert(signal2)

    assert should_alert
    assert "Direction changed" in reason


def test_invalidation_flow(
    temp_state_file: Path,
) -> None:
    sm = SignalStateMachine(filepath=temp_state_file)

    sm.transition_alert(make_buy_signal())
    assert sm.state == SignalState.ALERT_SENT

    sm.transition_invalidated("Setup failed conditions")

    assert sm.state == SignalState.INVALIDATED

    sm.transition_wait("Reset to wait state")

    assert sm.state == SignalState.WAIT


def test_material_entry_delta_triggers_alert(
    temp_state_file: Path,
) -> None:
    sm = SignalStateMachine(filepath=temp_state_file)

    signal1 = make_buy_signal(
        entry=2350.0,
        stop=2345.0,
        target=2360.0,
        timestamp=1000.0,
    )
    sm.transition_alert(signal1)

    signal2 = make_buy_signal(
        entry=2360.0,
        stop=2355.0,
        target=2380.0,
        timestamp=1005.0,
    )

    should_alert, reason = sm.should_alert(signal2)

    assert should_alert
    assert "Material entry change" in reason


def test_state_persists_after_alert(
    temp_state_file: Path,
) -> None:
    signal = make_buy_signal()

    sm = SignalStateMachine(filepath=temp_state_file)
    sm.transition_alert(signal)

    reloaded = SignalStateMachine(filepath=temp_state_file)

    assert reloaded.state == SignalState.ALERT_SENT

