# Drift Detection Tooling

This directory contains first-pass drift analysis tooling for comparing implementation manifests against authoritative Nexus NC1 contract artifacts.

## Authority model

- Nexus contract files are authoritative.
- Drift reports identify differences between declared contract and observed/extracted implementation surfaces.
- Drift tooling does **not** auto-promote observed behavior into contract authority.

## Phase 3 contents

- `implementation_manifest.schema.json`
  - schema for firmware-emitted declaration snapshots
- `validate_manifest_against_schema.py`
  - validates manifest structure against the schema
- `compare_manifest_to_contract.py`
  - compares manifest to NC1 contract and reports contract violations plus advisory extension/experimental findings
- `examples/sample_nc1_impl_manifest.json`
  - valid sample implementation manifest with intentional drift
- `examples/nc1_real_impl_manifest.json`
  - real-format NexCore declaration manifest for bridge validation
- `examples/sample_drift_report.md`
  - sample report generated from the intentionally drifting sample manifest

## Usage

```bash
python tools/drift/validate_manifest_against_schema.py \
  --manifest tools/drift/examples/nc1_real_impl_manifest.json

python tools/drift/compare_manifest_to_contract.py \
  --manifest tools/drift/examples/nc1_real_impl_manifest.json
```

Use `--allow-drift` for dry-run scenarios where contract violations should not fail CI.
