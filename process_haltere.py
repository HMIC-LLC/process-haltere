#!/usr/bin/env python3
"""Deterministic elapsed-time plausibility check for ongoing processes."""
from __future__ import annotations

import argparse
import json
import math


def evaluate(
    remaining_units: int,
    seconds_per_unit_low: float,
    seconds_per_unit_high: float,
    elapsed_since_progress_seconds: float,
    concurrency: int = 1,
    start_block: int | None = None,
    current_block: int | None = None,
) -> dict:
    if remaining_units < 0:
        raise ValueError("remaining_units must be nonnegative")
    if seconds_per_unit_low <= 0 or seconds_per_unit_high <= 0:
        raise ValueError("seconds-per-unit estimates must be positive")
    if seconds_per_unit_low > seconds_per_unit_high:
        raise ValueError("low estimate cannot exceed high estimate")
    if elapsed_since_progress_seconds < 0:
        raise ValueError("elapsed time must be nonnegative")
    if concurrency < 1:
        raise ValueError("concurrency must be at least one")

    waves = math.ceil(remaining_units / concurrency) if remaining_units else 0
    low_remaining = waves * seconds_per_unit_low
    high_remaining = waves * seconds_per_unit_high
    progress_ratio = elapsed_since_progress_seconds / seconds_per_unit_high
    remaining_ratio = (
        elapsed_since_progress_seconds / high_remaining if high_remaining else 0.0
    )

    if remaining_units == 0:
        classification = "COMPLETE"
    elif progress_ratio > 2 or remaining_ratio > 2:
        classification = "HALTERE_RED_FLAG"
    elif progress_ratio > 1:
        classification = "HALTERE_WARNING"
    else:
        classification = "NOMINAL"

    block_delta = None
    if start_block is not None or current_block is not None:
        if start_block is None or current_block is None:
            raise ValueError("start_block and current_block must be supplied together")
        if current_block < start_block:
            raise ValueError("current_block cannot precede start_block")
        block_delta = current_block - start_block

    return {
        "classification": classification,
        "remaining_units": remaining_units,
        "concurrency": concurrency,
        "expected_seconds_per_unit": {
            "low": seconds_per_unit_low,
            "high": seconds_per_unit_high,
        },
        "expected_remaining_seconds": {
            "low": low_remaining,
            "high": high_remaining,
        },
        "elapsed_since_durable_progress_seconds": elapsed_since_progress_seconds,
        "progress_delay_ratio": round(progress_ratio, 3),
        "remaining_envelope_ratio": round(remaining_ratio, 3),
        "block_delta": block_delta,
        "blockheight_policy": "provenance_only_never_elapsed_or_eta",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remaining-units", type=int, required=True)
    parser.add_argument("--seconds-per-unit-low", type=float, required=True)
    parser.add_argument("--seconds-per-unit-high", type=float, required=True)
    parser.add_argument("--elapsed-since-progress-seconds", type=float, required=True)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--start-block", type=int)
    parser.add_argument("--current-block", type=int)
    args = parser.parse_args()
    print(
        json.dumps(
            evaluate(
                remaining_units=args.remaining_units,
                seconds_per_unit_low=args.seconds_per_unit_low,
                seconds_per_unit_high=args.seconds_per_unit_high,
                elapsed_since_progress_seconds=args.elapsed_since_progress_seconds,
                concurrency=args.concurrency,
                start_block=args.start_block,
                current_block=args.current_block,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
