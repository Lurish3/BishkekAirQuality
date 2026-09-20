"""Generate SYNTHETIC demo data. These numbers are invented and are NOT real measurements.

Usage: python scripts/make_sample_data.py [output.csv]
"""

from __future__ import annotations

import math
import random
import sys
from datetime import date, timedelta
from pathlib import Path


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/sample/synthetic.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)

    lines = ["datetime,pm25"]
    day = date(2022, 1, 1)
    while day <= date(2023, 12, 31):
        # invented seasonal pattern: peak around January, minimum around July
        base = 50 + 40 * math.cos(2 * math.pi * (day.timetuple().tm_yday - 15) / 365)
        value = max(3.0, base + rng.gauss(0, 8))
        lines.append(f"{day.isoformat()} 12:00,{value:.1f}")
        day += timedelta(days=1)

    # deliberately dirty rows to exercise the cleaning step
    lines.append("2023-03-05 12:00,-999")
    lines.append("2023-03-06 12:00,")
    lines.append("2022-01-01 12:00,999")  # duplicate timestamp

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} (synthetic data)")


if __name__ == "__main__":
    main()
