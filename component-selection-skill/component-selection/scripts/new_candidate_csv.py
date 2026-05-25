#!/usr/bin/env python3
"""Create an empty electronic component candidate CSV with fixed base columns."""

import argparse
import csv
import re
from pathlib import Path


COLUMNS = [
    "rank",
    "part_number",
    "manufacturer",
    "component_type",
    "package",
    "production_status",
    "fit_summary",
    "lifecycle",
    "datasheet_url",
    "risks",
    "validation_needed",
    "score",
]

PARAM_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def parse_params(raw: str | None, fixed_columns: list[str]) -> list[str]:
    if not raw:
        return []
    params = [item.strip() for item in raw.split(",")]
    if any(not item for item in params):
        raise SystemExit("--params contains an empty column name.")
    invalid = [item for item in params if not PARAM_RE.fullmatch(item)]
    if invalid:
        raise SystemExit(
            "Invalid parameter column name(s): "
            + ", ".join(invalid)
            + ". Use snake_case starting with a lowercase letter."
        )
    if len(set(params)) != len(params):
        raise SystemExit("Duplicate parameter column in --params.")
    conflicts = [item for item in params if item in fixed_columns]
    if conflicts:
        raise SystemExit(f"Parameter columns conflict with fixed columns: {', '.join(conflicts)}")
    return params


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="Output CSV path.")
    parser.add_argument(
        "--params",
        help="Comma-separated dynamic parameter columns to insert after fit_summary.",
    )
    args = parser.parse_args()

    columns = list(COLUMNS)
    params = parse_params(args.params, columns)
    if params:
        insert_at = columns.index("lifecycle")
        columns[insert_at:insert_at] = params

    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()


if __name__ == "__main__":
    main()
