# Time-Crystal experiment checkpoint

These are optional reference experiments, not a completed physical engine.

## Reproduce from the repository root

```text
uv sync --group test --group lint --extra scientific --extra visualization
uv run python scripts/report_time_crystal_subsystem.py --output artifacts/time-crystal
```

## Validation

```text
uv run python -m pytest -q tests/test_time_crystal_clock_subsystem.py tests/test_canonical_polarity_clock.py
```

The dedicated workflow repeats these commands. Full generated traces and figures
are written under `artifacts/time-crystal`; they are not required to run the tests.
The checked-in summary records the original bounded results, including failures.
Reproduction regenerates evidence; it does not certify hardware or omitted physics.

## Reference documents

- [time_crystal_clock_subsystem_v0.1](../time_crystal_clock_subsystem_v0.1.md)
- [crystal-research-fit](../crystal-research-fit.md)
