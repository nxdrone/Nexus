# NC1 Scope

## In scope for the NC1 contract

- canonical profile identity and package metadata
- capability model including required/optional/extension/experimental classes
- command catalog and command behavior contract expectations
- structured config/discovery and commissioning workflow definitions
- client-visible state and safety semantic model
- canonical safety state presentation semantics (color + pattern intent), including precedence and FAILSAFE override behavior
- service/test discovery and compatibility/compliance declarations

## Out of scope for the NC1 contract

- NexBus wire/protocol implementation details
- NexCore internal module boundaries and scheduler details
- NexSight UI layout/design decisions
- implementation-private diagnostics that are not declared as contract surfaces

## Implementation-specific but allowed

The following can remain implementation-specific as long as external behavior still conforms to NC1 contract semantics:
- internal substate models mapped to public NC1 states
- hardware-specific optimization strategies
- optional extension features explicitly declared via capability support flags

## Transport/protocol-specific but referenced

NC1 may reference transport/protocol dependencies and minimum compatibility requirements, but transport behavior remains authoritative in NexBus artifacts.
