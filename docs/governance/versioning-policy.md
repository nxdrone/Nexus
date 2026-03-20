# Versioning Policy

## Objectives

- Provide predictable change management for producers and consumers.
- Make compatibility intent explicit at profile and artifact levels.

## Baseline policy

- Every contract package and major artifact carries a version field.
- Backward-incompatible changes require explicit major-version signaling.
- Additive, backward-compatible changes should use minor-version increments.
- Clarifications/fixes with no behavioral surface impact may use patch-version increments.

## Stability markers

Contract elements should include lifecycle markers (e.g., draft, experimental, stable, deprecated) where relevant.

## TODO

Define exact versioning mechanics per artifact class and release process for NC1 and future profiles.
