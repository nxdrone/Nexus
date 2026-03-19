# Drift Detection Tooling

This directory contains first-pass drift analysis tooling for comparing an implementation manifest against authoritative Nexus NC1 contract artifacts.

## Authority model

- Nexus contract files are authoritative.
- Drift reports identify differences between declared contract and observed/extracted implementation surfaces.
- Drift tooling does **not** auto-promote observed behavior into contract authority.

## Phase 3 contents

- `implementation_manifest.schema.json`
  - neutral schema for implementation surface manifests
- `compare_manifest_to_contract.py`
  - compares manifest to NC1 contract and reports missing/unknown/mismatched surfaces
- `examples/sample_nc1_impl_manifest.json`
  - valid sample implementation manifest with intentional drift
- `examples/sample_drift_report.md`
  - sample report generated from the example manifest

## Usage

```bash
python tools/drift/compare_manifest_to_contract.py \
  --manifest tools/drift/examples/sample_nc1_impl_manifest.json
```

Use `--allow-drift` for dry-run scenarios where reporting should not fail CI.
