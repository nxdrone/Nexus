# Change Management Policy

## 1. Overview

This policy defines how contract changes are introduced and propagated across the Nexus ecosystem.

Nexus defines the contract, implementations declare what they support, Nexus tooling validates alignment, and clients consume contract-defined behavior.

**Core principle:** **"Nexus defines the contract. Implementations must conform to it."**

---

## 2. Core Change Flow

Any new feature, command, capability, board-specific contract surface, or profile addition must follow this sequence:

1. Define in Nexus (contract update)
2. Validate in Nexus
3. Implement in NexCore
4. Validate implementation declaration against Nexus
5. Consume in NexSight

This order is mandatory and must not be reversed. Firmware behavior must not independently define contract behavior.

```text
Nexus -> NexCore -> Nexus Validation -> NexSight
```

---

## 3. Feature Introduction Workflow

When introducing a new feature:

1. Update relevant contract artifacts in Nexus (for example: `commands.json`, `capabilities.json`, `config.schema.json`, commissioning/state/test/compatibility files).
2. Assign a stability tier:
   - `experimental`
   - `extension`
   - `contract_required`
3. Update shared or profile schemas only where needed and with explicit intent.
4. Update compliance expectations and test-case scaffolding.
5. Run Nexus validation tooling (schema + consistency checks).

After Nexus contract validation passes:

6. Implement the feature in NexCore.
7. Declare support in the implementation manifest.
8. Run manifest validation and drift comparison against Nexus.

After implementation declaration is validated:

9. Expose feature behavior in NexSight based on declared capabilities and the Nexus contract (not on undocumented behavior).

---

## 4. Board Introduction Workflow

When introducing a new board:

1. Determine whether the board fits an existing profile (for example, NC1).
2. Do **not** create a new profile unless contract meaning changes.
3. Represent board differences through client-visible contract elements only:
   - identity
   - capabilities
   - config model
   - test model

Rules:

- Nexus models only client-visible differences.
- NexCore declares actual board capabilities at runtime.
- NexSight adapts using capability detection and declared contract, not board-specific hardcoding.

---

## 5. Stability Tiers

### `experimental`

- Not stable.
- Not for normal client dependence.
- May change without compatibility guarantees.

### `extension`

- Defined in Nexus.
- Optional for implementations.
- Safe for clients to ignore unless explicitly needed.

### `contract_required`

- Baseline required behavior.
- Required for compliance.
- Safe for clients to depend on as profile baseline.

### Promotion path

`experimental` -> `extension` -> `contract_required`

Promotion requires explicit contract updates, validation updates, and compatibility review.

---

## 6. Contract Authority Rules

- Nexus is the authoritative contract source.
- Firmware declarations are declarations of implementation support, not authority.
- Drift tooling detects mismatches; it does not redefine contract truth.

The following are explicitly forbidden:

- Schema changes originating from firmware behavior alone.
- Silent contract expansion in implementations.
- Client reliance on undocumented or non-declared behavior.

---

## 7. Validation Requirements

The following validation steps are required:

1. Nexus contract validation (schema + consistency).
2. Implementation manifest validation.
3. Drift comparison against authoritative contract artifacts.

Accepted outcomes:

- **Fully compliant**: no contract violations.
- **Compliant with extensions**: required surface is compliant; optional extension surface is declared and understood.
- **Non-compliant**: contract violations exist and must be fixed before release integration.

---

## 8. Prototyping Rules

Firmware-first experimentation is allowed only under strict constraints:

- Experimental features must be clearly marked as experimental.
- Experimental features must not be treated as stable contract surface.
- Experimental features must not be required by clients.
- Experimental behavior must be formalized in Nexus before it can be treated as contract.

---

## 9. Release Discipline

Release propagation chain:

**Nexus -> NexCore -> Nexus validation -> NexSight**

Release rules:

- Contract changes must be versioned.
- Compatibility impact must be evaluated and documented.
- Breaking changes must be explicit and intentional.
- Consumers must not ship dependencies on behavior that is not ratified in Nexus.

---

## 10. Summary Principle

**New behavior is defined in Nexus, declared by implementations, validated by Nexus tooling, and only then consumed by clients.**
