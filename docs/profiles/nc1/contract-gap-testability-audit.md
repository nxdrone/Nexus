# NC1 Contract-Gap and Testability Audit

## Purpose

This audit answers two questions:

1. What client-visible or testable functionality appears to exist in NexCore but is not yet properly represented in the Nexus NC1 contract package?
2. What automated tests should be added in NexCore and Nexus so NexSight's Tests page reflects real firmware-supported, contract-declared, testable behavior?

This document is a focused planning artifact. It does not redefine contract authority.

---

## Inputs reviewed

- NC1 contract package (`contracts/profiles/nc1/*`)
- NC1 compliance scaffolding (`tools/compliance/nc1/*`)
- Drift tooling and real implementation manifest example (`tools/drift/*`)

Observed manifest facts used in this audit:

- NexCore declares baseline required capabilities and commands.
- NexCore also declares support for `state_control.test_mode` and `telemetry.stream_runtime`.
- NexCore includes generic command-completion metadata (`default_timeout_ms`, `supports_progress_updates`).

---

## 1) Audit: NexCore-visible functionality vs Nexus NC1 contract

### Classification legend

- **Adequately modeled**: already in Nexus with useful client/compliance semantics.
- **Missing**: appears present in implementation surface but not modeled in contract.
- **Partially modeled**: present but lacks enough contract detail for strong validation/UI.
- **Implementation-only**: internal concern; should stay out of contract.
- **Experimental hold**: known but should not be promoted yet.

### Audit matrix

| Area | Current contract status | Classification | Notes / rationale |
|---|---|---|---|
| Required command baseline (`system.get_profile`, `config.*`, commissioning core, `test.list_catalog`, `safety.stop_all`) | Explicit in `commands.json` + `compatibility.json` | Adequately modeled | Baseline command presence and high-level behavior are contract-declared. |
| Component test execution (`test.run_component`) | Declared as optional command and testing capability context | Partially modeled | Catalog/discovery is strong, but run lifecycle/result schema semantics remain coarse (progress/result taxonomy not ratified). |
| Test-mode control (`state.enter_test_mode`, `state.exit_test_mode`) | Declared as extension command surface + state model references | Partially modeled | Preconditions and transitions are present, but blocked-reason taxonomy and acknowledgement semantics need tighter contract language. |
| Test catalog metadata | `test.schema.json` includes hazard, availability, blocked reasons, session gating | Partially modeled | Missing explicit fields for determinism/repeatability, expected side effects, and operator role requirements that would improve NexSight rendering and automation confidence. |
| Command completion semantics | Manifest has global completion hints | Missing | Contract defines per-command completion model textually, but no shared structured completion schema links timeout/progress/terminal outcome expectations. |
| Workflow-style tests/calibrations (guided flows) | Only generic commissioning/test references | Missing | No explicit workflow contract shape (steps, abort/resume semantics, required evidence) for operator-guided routines. |
| Diagnostic/self-test surfaces | Indirectly covered by test catalog concept | Partially modeled | Need explicit test categories + result-classification contract (pass/fail/inconclusive/interrupted/error codes). |
| Config model group boundaries | Good separation of read-only vs writable/stage-bound groups | Adequately modeled | Useful baseline exists for discovery/config distinction. |
| Config field-level mutability and constraints | Group-level structure exists | Partially modeled | Per-field constraints/units/ranges/defaults are not yet ratified; limits automated validation and UI affordances. |
| Commissioning reset behavior | Present but explicitly unratified | Experimental hold | Correctly marked as implementation-specific command hint. |
| State transitions and semantics (`safe/armed/test_mode/failsafe/signal_loss`) | Explicit state model with limits | Adequately modeled | Good client semantics baseline. |
| State blocked-reason semantics | Blocked reasons exist for test catalog; transition blockers less formalized | Partially modeled | Need shared blocker code registry across commissioning/state/test transitions for consistent UX/compliance. |
| Telemetry stream capability | Declared as extension capability in contract, supported in manifest | Partially modeled | Capability exists, but contract does not yet define minimum transport-agnostic telemetry discovery fields. |
| Firmware internal algorithms/tuning internals | Not modeled | Implementation-only | Should remain out of contract unless client-visible behavior depends on it. |

---

## 2) Proposed Nexus contract additions/clarifications

Only promote client-relevant, stable-enough behavior.

### A. Structured command completion contract

- **Add**: `contracts/profiles/nc1/commands.completion.schema.json` (or equivalent section in `commands.json`) defining terminal statuses, progress event shape, timeout behavior, and cancellation/stop interaction.
- **Tier**: `extension` initially (promote to `contract_required` after implementation convergence).
- **Why it matters**: Removes UI/client heuristics around progress bars, timeout handling, and result interpretation.
- **NexSight value**: Consistent run UX and clear completion/error banners.

### B. Test result taxonomy + evidence hints

- **Add**: Extend `test.schema.json` with ratified result classes (`pass`, `fail`, `inconclusive`, `interrupted`, `error`) and optional evidence descriptors.
- **Tier**: `contract_required` for result class, `extension` for richer evidence payload hints.
- **Why it matters**: Enables meaningful history/reporting rather than binary success assumptions.
- **NexSight value**: Better filtering, summaries, and actionability on failed tests.

### C. Workflow test model (guided flows)

- **Add**: New workflow/test-flow contract section (step list, prerequisites, abort/resume/retry behavior, expected operator actions).
- **Tier**: `extension`.
- **Why it matters**: Captures real guided procedures (calibration-style flows) in a contract-driven way.
- **NexSight value**: Can render step-driven workflows without firmware-specific hardcoding.

### D. Shared blocked-reason vocabulary

- **Add**: Cross-domain blocker code registry referenced by commissioning, state transitions, and test availability.
- **Tier**: `contract_required` for core codes; `extension` for profile-specific extras.
- **Why it matters**: Prevents fragmented reasons and inconsistent client messaging.
- **NexSight value**: Uniform blocked-state UI and remediation guidance.

### E. Field-level config metadata ratification

- **Add**: Incremental extension to config schema for field constraints (type/unit/min/max/enum/default/visibility).
- **Tier**: `extension` first; promote critical fields used by commissioning to `contract_required` later.
- **Why it matters**: Improves validation and prevents invalid writes.
- **NexSight value**: Safer editors and richer form generation.

### F. Telemetry discovery minimum (if client-facing consumption is planned)

- **Add**: Minimal extension contract for telemetry channel discovery metadata (channel id, sample class, units, update mode).
- **Tier**: `extension`.
- **Why it matters**: Makes declared telemetry capability actionable.
- **NexSight value**: Can selectively surface runtime indicators without custom firmware parsing.

---

## 3) Proposed NexCore automated test strategy

### Command-level unit/integration

1. **`test_required_command_presence_manifest_sync`**  
   - Validates required commands exposed by firmware match declared manifest/contract baseline.  
   - Type: integration/harness.  
   - Value: catches declaration drift.  
   - NexSight impact: indirect (prevents missing UI actions).

2. **`test_command_completion_terminal_outcomes`**  
   - Validates emitted completion states for async commands and timeout behavior.  
   - Type: integration/simulation.  
   - Value: hardens completion semantics.  
   - NexSight impact: direct (progress/completion UI correctness).

### Config/commissioning

3. **`test_config_group_mutability_enforced`**  
   - Ensures read-only groups reject writes; writable groups accept valid updates.  
   - Type: integration.  
   - Value: contract compliance baseline.  
   - NexSight impact: direct (prevents false editable controls).

4. **`test_commissioning_stage_blockers_and_clearance`**  
   - Validates stage blockers appear when required data missing and clear when satisfied.  
   - Type: integration/harness.  
   - Value: prevents dead-end commissioning behavior.  
   - NexSight impact: direct (guided stage UX).

5. **`test_commissioning_commit_requires_ready_state`**  
   - Validates commit refusal outside `ready_to_commit` and success path includes refresh signal.  
   - Type: integration.  
   - Value: guards critical workflow guarantees.  
   - NexSight impact: direct.

### State/safety/test mode

6. **`test_stop_all_interrupts_active_tests`**  
   - Ensures `safety.stop_all` interrupts test runs and emits interrupted completion.  
   - Type: integration/simulation.  
   - Value: safety-critical.  
   - NexSight impact: direct (operator trust).

7. **`test_test_mode_transition_blocked_reasons`**  
   - Validates blocked reason codes for denied enter/exit test mode transitions.  
   - Type: integration.  
   - Value: avoids opaque rejections.  
   - NexSight impact: direct.

### Test catalog + workflow

8. **`test_catalog_metadata_completeness`**  
   - Validates each catalog entry includes required metadata and valid hazard/availability values.  
   - Type: unit + contract fixture check.  
   - Value: improves discovery quality.  
   - NexSight impact: direct.

9. **`test_guided_workflow_step_integrity`** (when workflow contract lands)  
   - Validates step order, required actions, and abort/resume transitions.  
   - Type: simulation/harness.  
   - Value: prevents workflow regressions.  
   - NexSight impact: direct.

### Regression coverage

10. **`test_regression_recent_blocker_code_bug_*`**  
    - Add focused tests for known recent bugs (code mismatch, missing completion payload, stale availability, etc.).  
    - Type: targeted regression tests.  
    - Value: keeps known failures from returning.  
    - NexSight impact: varies; often high for trust.

---

## 4) Proposed Nexus compliance/tests strategy

| Check name | Enforces | Best location | Gate recommendation |
|---|---|---|---|
| `check_required_command_completion_metadata` | Required commands include ratified completion semantics once schema added | Consistency checks + schema validation | Warn initially, then block |
| `check_test_catalog_required_metadata` | Required test metadata present and enums valid | Consistency checks/compliance test case | Block baseline |
| `check_blocked_reason_code_registry_usage` | Only registered blocker codes used across test/state/commissioning | Consistency checks | Warn initially |
| `check_commissioning_commit_observable_effects` | Commit expectations include post-commit refresh/state signal semantics | Compliance manifest + future live harness | Block for baseline once harness exists |
| `check_stop_all_interrupt_expectation` | Test model includes stop-all interrupt behavior declaration | Compliance test case | Block baseline |
| `check_extension_surfaces_declared_not_required` | Optional/extension/experimental surfaces not treated as baseline required | Drift comparator + compliance manifest | Block baseline |
| `check_manifest_declared_capability_command_alignment` | Manifest command/capability declarations align with contract tiers and references | Drift logic | Block baseline |
| `check_workflow_definition_integrity` (future) | Guided workflow steps and gating metadata complete | Schema + consistency checks | Warn until ratified |

### Immediate compliance file updates recommended

- Extend `tools/compliance/nc1/test_cases/required_commands.json` with completion semantics expectations for required async/staged commands.
- Add `tools/compliance/nc1/test_cases/test_catalog_expectations.json` for hazard/gating/availability/result taxonomy checks.
- Add `tools/compliance/nc1/test_cases/blocked_reason_expectations.json` for cross-domain blocker consistency.

---

## 5) Mapping to NexSight Tests page

Only operator-useful, contract-declared tests/workflows should appear in the Tests page.

| Candidate surface | Show in Tests page? | Audience | Needed metadata | Contract sufficiency |
|---|---|---|---|---|
| Component tests from catalog | Yes | Operator-facing + service-facing | display name, hazard class, availability, blocked reasons, expected duration, stop-all support | Mostly sufficient; add result taxonomy/evidence hints |
| Guided calibration/workflow tests | Yes (once ratified) | Operator-facing/service-facing | ordered steps, prerequisites, operator actions, abort/resume rules | Needs extension |
| Safety stop validation routine (service) | Yes (if catalog-declared) | Service-facing | hazard, gating, expected interruption behavior | Needs clearer test outcome semantics |
| Commissioning verification checks | Yes (subset) | Operator-facing | stage mapping, blocker codes, pass criteria | Partially sufficient; better blocker registry needed |
| Developer diagnostics/self-check internals | No (default) | Developer-only | internal metrics/logs | Should remain non-UI unless promoted |
| Contract/compliance-only checks | No | Contract/compliance-only | N/A | Keep in CI/compliance tooling |
| Low-level telemetry channel probes | Usually no (or separate diagnostics page) | Developer/service | channel metadata + sampling semantics | Needs extension and product decision |

### What should NOT be in Tests page

- Internal unit-level sanity checks.
- Firmware-only diagnostics without operator actionability.
- Experimental tests not explicitly marked and gated.
- Contract compliance checks that are governance-only and not actionable for operators.

---

## 6) Prioritized implementation plan

### High priority

1. **Ratify test result taxonomy + required catalog metadata completeness checks in Nexus.**
2. **Add NexCore tests for stop-all interruption, commissioning stage blockers, and commit-readiness enforcement.**
3. **Add Nexus compliance test cases for test catalog quality and required command completion behavior.**
4. **Ensure NexSight Tests page consumes hazard/gating/availability/blocked reasons from contract-declared catalog only.**

### Medium priority

1. **Add shared blocked-reason registry and align commissioning/state/test surfaces.**
2. **Add field-level config metadata for key commissioning-critical fields.**
3. **Add NexCore tests for test-mode transition blocker specificity and metadata consistency.**
4. **Introduce initial guided workflow contract model as extension.**

### Low priority

1. **Telemetry discovery contract expansion for future diagnostics experiences.**
2. **Deeper simulation tests for rare runtime/timing edge cases not currently user-facing.**
3. **Promotion of mature extensions to contract_required after empirical stability period.**

### Recommended execution order across repos

1. **Nexus**: ratify minimal contract additions (result taxonomy, completion semantics, blocker vocabulary).  
2. **NexCore**: implement/expand automated tests aligned to new/clarified contract checks.  
3. **Nexus**: add compliance and drift checks to enforce new requirements.  
4. **NexSight**: consume newly ratified metadata for a cleaner Tests page (without using non-contract heuristics).

---

## Final summary

- The NC1 contract is strong for baseline command/capability/state structure, but test lifecycle semantics, blocked-reason normalization, and guided workflow modeling are the highest-value gaps.
- The most important missing automated coverage is around safety interruption, commissioning progression/commit semantics, and test catalog quality guarantees.
- The Tests page should prioritize operator/service-relevant cataloged tests and workflows, while excluding internal and compliance-only checks.
- Nexus should continue to ratify only stable, client-relevant behavior; implementation quirks should remain out of contract unless intentionally promoted.
