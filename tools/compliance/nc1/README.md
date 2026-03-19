# NC1 Compliance Tooling

This directory provides the first-pass NC1 compliance harness scaffolding for Nexus.

## Authority and intent

- Nexus contract artifacts remain authoritative.
- Compliance checks evaluate implementations against those declared artifacts.
- Compliance tooling reports pass/fail evidence; it does **not** redefine the contract.

## Phase 3 contents

- `compliance_manifest.json`
  - machine-readable compliance target metadata and required surfaces
- `test_cases/required_commands.json`
  - baseline required command behavior expectations
- `test_cases/required_capabilities.json`
  - required capability declarations and support expectations
- `test_cases/state_model_expectations.json`
  - contract-level state/safety expectations
- `test_cases/commissioning_expectations.json`
  - commissioning workflow expectations

## Current scope

This scaffolding is contract-derived and transport-agnostic.
It does not yet execute live checks against NexCore targets.

## Future direction

Next phases can add runners/adapters that ingest implementation responses and evaluate these test case definitions directly.
