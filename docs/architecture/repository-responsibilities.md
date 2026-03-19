# Repository Responsibilities

## Responsibility split

### `nexus`
- Owns ecosystem contract definitions and schemas.
- Owns compatibility/version policy and compliance declarations.
- Owns validation/compliance/drift tooling definitions.

### Nexbus
- Owns protocol and transport implementation.
- Must carry contract-defined payloads and semantics.
- Does not own or redefine client-facing contract surface.

### NexCore_* repositories
- Own firmware implementations of declared profiles.
- Must implement required capabilities/commands/state/config behavior from `nexus`.
- Must pass compliance validation against `nexus` definitions.

### NexSight
- Owns client/tooling consumption of declared contracts.
- Should rely on explicit profile declarations, not implementation heuristics.

## Why contracts live here

Contracts are centralized in `nexus` so all producers and consumers can share one auditable, versioned source of truth.
