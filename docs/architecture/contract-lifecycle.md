# Contract Lifecycle

## Lifecycle flow

1. **Propose**
   - Add or modify contract/schema definitions in Nexus.
   - Mark maturity status (e.g., draft, experimental, stable).
2. **Review**
   - Validate cross-repo impact (NexBus, NexCore, NexSight).
   - Confirm compatibility/version policy implications.
3. **Publish**
   - Merge updated contract artifacts and policy notes.
   - Communicate target implementation/consumer adoption windows.
4. **Implement/Consume**
   - Downstream repos align behavior to published contract.
5. **Validate & Monitor**
   - Run validation, compliance, and drift tooling.
   - Open follow-up contract changes in Nexus when required.

## Change direction rule

Contract changes flow from Nexus to implementations/consumers.
Observed implementation behavior can inform proposals, but does not become official contract without explicit declaration in Nexus.
