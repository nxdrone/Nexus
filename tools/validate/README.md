# Contract Validation Tooling

This directory contains validation tooling for Nexus contract artifacts.

## Authority model

Nexus contract files are authoritative.
These tools validate declared contract artifacts and report issues.
They **do not** infer, rewrite, or promote implementation behavior into authoritative contract.

## What exists in phase 3

- `contracts/validate_contracts.py`
  - loads NC1 contract files
  - checks JSON integrity
  - validates contract structures against shared schemas where applicable
  - runs internal consistency checks across NC1 files
  - emits errors and warnings with file/path context
- `contracts/consistency_checks.py`
  - cross-file checks for references, duplicates, stability vocabulary, and key invariants
- `shared/`
  - reusable loaders, schema helpers, and reporting model

## Local usage

From repository root:

```bash
python tools/validate/contracts/validate_contracts.py
```

Expected behavior:
- exit code `0` on success or warnings only
- exit code `1` if validation/consistency errors exist

## Extension notes

The validator is currently NC1-first, but is structured so additional profile bundles can be added with new file maps and profile-aware checks.
