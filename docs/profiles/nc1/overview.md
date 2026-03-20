# NC1 Profile Overview

NC1 is the first concrete profile package in Nexus and defines the canonical client-facing interoperability contract for NC1-class implementations.

## What NC1 governs

The NC1 package governs:
- profile identity and compatibility declarations
- capability declarations and support semantics
- command catalog tokens, stability classes, and behavior expectations
- configuration and commissioning contract structures
- state/safety semantics exposed to clients
- test/service discovery contract shape

## Producer/consumer relationship

- **NexCore** implementations publish and execute NC1 contract surfaces.
- **NexSight** and other clients consume NC1 contract declarations to drive UX and automation behavior.
- **NexBus** carries data and command traffic, while NC1 in Nexus defines the interop contract those payloads represent.

## Boundary reminder

NC1 in Nexus defines contract intent and client-visible semantics; it does not define firmware internals, transport implementation specifics, or product-specific UX flows.

## Safety state presentation contract

NC1 includes a canonical state presentation contract in `contracts/profiles/nc1/state-presentation.json` that maps NC1 state-machine states to safety-critical color and pattern intent semantics. This mapping is authoritative for ecosystem consistency and must not be remapped by tools or firmware for safety states.

The presentation contract also defines:
- explicit state priority for deterministic precedence resolution
- explicit combined-state composition for `armed+test_mode`
- safety-level classification (`safe`, `caution`, `hazard`, `fault`, `unknown`)
- accessibility metadata for visibility support
- a mandatory FAILSAFE override rule for fault-state dominance

