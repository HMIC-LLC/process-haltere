# Process Haltere

A small Python calculator for checking whether an ongoing batch has gone too long without **durable progress**. It turns a supplied per-unit time range, remaining work count, concurrency, and time since the last completed artifact into a timing classification. It uses only the standard library.

`RUNNING` is a separate question. This calculator does **not** inspect a process, verify remote execution, discover the last progress event, or prove that work is still moving. The caller must supply trustworthy observations. If those are unavailable, report the execution state as unverified rather than treating a `NOMINAL` calculation as proof of motion.

## Use

Requires Python 3.10 or newer.

```powershell
python process_haltere.py --remaining-units 11 --seconds-per-unit-low 180 --seconds-per-unit-high 240 --elapsed-since-progress-seconds 300 --concurrency 1
```

The command prints JSON. `evaluate(...)` exposes the same calculation for Python callers. The returned `classification` is `NOMINAL`, `HALTERE_WARNING`, `HALTERE_RED_FLAG`, or `COMPLETE`.

The expected remaining range is `ceil(remaining_units / concurrency) * seconds_per_unit`. A warning begins when the no-progress interval exceeds the upper per-unit estimate. A red flag begins when it exceeds twice that estimate or twice the upper estimate for the remaining batch. These thresholds are strict `>` comparisons: equality does not trigger the next level.

If start and current block heights are supplied, their difference is recorded as provenance only. Block height is never converted into elapsed time or an ETA.

## Test

```powershell
python -m unittest -v test_process_haltere
```

The tests cover nominal, warning, red flag, complete, block-height, and threshold-boundary cases. No batch or remote service is launched.

## Origin and scope

This calculator was extracted from a larger private batch-status workflow. The public copy includes synthetic examples only. It is a timing component, not a monitoring service or operational status attestation.

## License

MIT. See `LICENSE`.

