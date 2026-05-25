#!/usr/bin/env python3
"""Rank electronic component candidates from manual score columns in a CSV file."""

import argparse
import csv
import sys
from pathlib import Path


DEFAULT_WEIGHTS = {
    "requirement": 0.35,
    "performance": 0.25,
    "fit": 0.15,
    "lifecycle": 0.15,
    "validation": 0.10,
}

LIFECYCLE_SCORE = {
    "preferred": 10.0,
    "new": 10.0,
    "production": 9.5,
    "active": 9.0,
    "preview": 8.0,
    "mature": 7.0,
    "unknown": 4.0,
    "nrnd": 2.0,
    "not_recommended_for_new_designs": 2.0,
    "not recommended for new designs": 2.0,
    "obsolete": 0.0,
    "eol": 0.0,
}


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.strip().replace("$", "").replace(",", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_weights(raw: str | None) -> dict[str, float]:
    weights = dict(DEFAULT_WEIGHTS)
    if not raw:
        return weights
    for item in raw.split(","):
        if not item.strip():
            continue
        key, sep, value = item.partition("=")
        if not sep:
            raise SystemExit(f"Invalid weight '{item}'. Use name=value.")
        key = key.strip().lower()
        if key not in weights:
            raise SystemExit(f"Unknown weight '{key}'. Valid keys: {', '.join(weights)}")
        parsed = parse_float(value)
        if parsed is None or parsed < 0:
            raise SystemExit(f"Invalid numeric weight for '{key}'.")
        weights[key] = parsed
    total = sum(weights.values())
    if total <= 0:
        raise SystemExit("At least one weight must be greater than zero.")
    return {key: value / total for key, value in weights.items()}


def clamp_score(value: float) -> float:
    return max(0.0, min(10.0, value))


def row_label(row: dict[str, str], index: int) -> str:
    return row.get("part_number") or row.get("part") or f"row {index}"


def read_score(
    row: dict[str, str],
    name: str,
    index: int,
    *,
    default: float | None = None,
) -> float | None:
    column = f"score_{name}"
    raw = row.get(column)
    parsed = parse_float(raw)
    if parsed is not None:
        clamped = clamp_score(parsed)
        if clamped != parsed:
            warn(f"{row_label(row, index)}: {column}={parsed:g} clamped to {clamped:g}.")
        return clamped
    if default is not None:
        warn(f"{row_label(row, index)}: missing or invalid {column}; using {default:g}.")
        return default
    return None


def lifecycle_score(row: dict[str, str], index: int) -> float:
    manual = read_score(row, "lifecycle", index)
    if manual is not None:
        return manual
    raw_status = row.get("lifecycle") or row.get("production_status") or "unknown"
    status = raw_status.strip().lower().replace("-", "_")
    score = LIFECYCLE_SCORE.get(status)
    if score is None:
        warn(f"{row_label(row, index)}: unknown lifecycle/production_status '{raw_status}'; using 4.")
        return 4.0
    return score


def rank_components(rows: list[dict[str, str]], weights: dict[str, float]) -> list[dict[str, str]]:
    ranked: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        scores = {
            "requirement": read_score(row, "requirement", index, default=5.0),
            "performance": read_score(row, "performance", index, default=5.0),
            "fit": read_score(row, "fit", index, default=5.0),
            "validation": read_score(row, "validation", index, default=5.0),
            "lifecycle": lifecycle_score(row, index),
        }
        total = sum(scores[key] * weights[key] for key in weights)
        result = dict(row)
        for key, value in scores.items():
            result[f"computed_{key}"] = f"{value:.2f}"
        result["weighted_score"] = f"{total:.2f}"
        ranked.append(result)

    return sorted(ranked, key=lambda item: float(item["weighted_score"]), reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path, help="Candidate component CSV file.")
    parser.add_argument("--out", type=Path, help="Output CSV path. Defaults to stdout.")
    parser.add_argument(
        "--weights",
        help="Comma-separated weights, e.g. requirement=0.35,performance=0.25,fit=0.15",
    )
    args = parser.parse_args()

    weights = parse_weights(args.weights)
    with args.csv_file.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("Input CSV has no candidate rows.")

    ranked = rank_components(rows, weights)
    fieldnames = list(ranked[0].keys())

    if args.out:
        with args.out.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ranked)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ranked)


if __name__ == "__main__":
    main()
