# Waves experiment checkpoint

These are optional reference experiments, not a completed physical engine.

## Reproduce from the repository root

```text
uv sync --group test --group lint --extra scientific --extra visualization
uv run python scripts/report_time_order_controls.py --output artifacts/waves
uv run python scripts/report_mode_pair_robustness.py --output artifacts/waves/mode-pair-robustness.json
uv run python scripts/report_multimode_wave_control.py --output artifacts/waves
```

## Validation

```text
uv run python -m pytest -q tests/test_time_order_diagnostics.py tests/test_proposed_nonlinear_wave_control.py tests/test_proposed_mode_pair_control.py tests/test_proposed_multimode_wave_control.py tests/test_proposed_scalar_wave_control.py
```

The dedicated workflow repeats these commands. Full generated traces and figures
are written under `artifacts/waves`; they are not required to run the tests.
The checked-in summary records the original bounded results, including failures.
Reproduction regenerates evidence; it does not certify hardware or omitted physics.

## Reference documents

- [time_order_and_wave_controls_v0.1](../time_order_and_wave_controls_v0.1.md)
- [mode_pair_robustness_v0.1](../mode_pair_robustness_v0.1.md)
- [multimode_wave_control_v0.1](../multimode_wave_control_v0.1.md)
