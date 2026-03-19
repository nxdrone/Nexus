# Nexus

Nexus is the canonical ecosystem contract and compliance layer for the Nexus robotics platform.

It is the authoritative source of truth for:
- ecosystem profile contracts
- machine-readable schemas
- compatibility and version policy
- compliance definitions
- drift detection and validation tooling
- examples and guidance for implementers and consumers

## What belongs in this repository

This repository owns **contract definitions** and **governance** for cross-repo interoperability.

Examples of in-scope content:
- profile packages (starting with NC1)
- shared schemas and profile schemas
- policy and lifecycle documentation
- validation/compliance/drift tooling
- examples illustrating intended contract usage

## What does not belong in this repository

This repository is **not**:
- a firmware implementation repository
- a protocol transport implementation repository
- a product UI/client implementation repository

Concretely, this repo does not contain runtime control logic from NexCore firmware, transport mechanics from NexBus, or product features from NexSight.

## Relationship to surrounding repositories

- **NexBus**: implements protocol and transport behavior that carries contract data.
- **NexCore**: firmware repositories that implement profile contracts on devices/controllers.
- **NexSight**: client/tooling ecosystem that discovers, configures, commands, and validates against declared contracts.
- **Nexus** (this repo): defines the contract those repos implement or consume.

## Contract-first philosophy

Contract-first means the canonical client-facing behavior must be declared in Nexus before it is treated as stable ecosystem surface.

Key principles:
1. If consumers depend on it, it must be defined here.
2. Implementation behavior does not automatically become contract.
3. Validation and compliance compare implementations to Nexus; they do not redefine Nexus from observed quirks.

## Long-term purpose

Over time, this repository should become the stable coordination layer across Nexus ecosystem components by:
- publishing profile contract packages with explicit lifecycle status
- defining shared schema vocabulary and compatibility policies
- enabling reproducible compliance validation
- detecting and preventing contract drift across implementations and consumers

## Current state

NC1 now includes a first-pass, structured contract package intended for implementation alignment in NexCore and consumption alignment in NexSight, with provisional areas explicitly marked for ratification in later phases.
