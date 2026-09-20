"""Small helpers that build tiny CSV files for tests. All numbers here are invented."""

from __future__ import annotations

from pathlib import Path


def write_csv(
    path: Path,
    rows: list[tuple[str, str]],
    header: tuple[str, str] = ("ts", "value"),
) -> Path:
    lines = [",".join(header)] + [f"{ts},{val}" for ts, val in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# Two full months with constant values: January 2023 = 100, July 2023 = 20.
SIMPLE_ROWS: list[tuple[str, str]] = [
    ("2023-01-01 00:00", "100"),
    ("2023-01-15 12:00", "100"),
    ("2023-01-31 23:00", "100"),
    ("2023-07-01 00:00", "20"),
    ("2023-07-15 12:00", "20"),
]
