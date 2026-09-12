from __future__ import annotations

import json
import time
from pathlib import Path

from market_data.synthetic_dxy import SyntheticDXY


CACHE_FILE = Path("runtime_cache/synthetic_dxy.json")
CACHE_TTL = 3600
H1_SECONDS = 3600


class DXYCache:
    @classmethod
    def load_or_build(cls, key: str, count: int = 200) -> list[float]:
        now = int(time.time())

        if CACHE_FILE.exists():
            try:
                payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                created_at = int(payload["created_at"])
                cache_candle = (created_at // H1_SECONDS) * H1_SECONDS
                current_candle = (now // H1_SECONDS) * H1_SECONDS
                values = [float(x) for x in payload["values"]]

                if (
                    len(values) >= count
                    and cache_candle == current_candle
                    and now - created_at < CACHE_TTL
                ):
                    print(
                        f"DXY CACHE HIT: age={now - created_at}s "
                        f"bars={len(values)}"
                    )
                    return values[-count:]
            except (OSError, ValueError, KeyError, TypeError):
                pass

        print("DXY CACHE MISS: refreshing Synthetic DXY")

        values = SyntheticDXY.build(key, count=count)

        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps(
                {
                    "created_at": now,
                    "values": values,
                },
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )

        print(f"DXY CACHE WRITE: bars={len(values)}")
        return values[-count:]
