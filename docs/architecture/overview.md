# Ecosystem Architecture Overview

Nexus sits at the ecosystem contract layer above implementation and consumer repositories.

## Layer model

1. **Contract Layer (Nexus)**
   - defines profile contracts
   - defines shared schemas and compatibility semantics
   - publishes governance and lifecycle policy
2. **Implementation Layers (NexBus, NexCore)**
   - implement transport and firmware behavior
   - must align to contract declarations from Nexus
3. **Consumer Layer (NexSight and other clients/tooling)**
   - consume declared contract surfaces
   - rely on compatibility and stability guarantees from Nexus

## Core architectural rule

Nexus defines the contract.
Implementations and consumers align to that contract.
Nexus does not derive authoritative contract behavior from implementation quirks.

## Initial scope

The first profile package in this repo is NC1, now defined as a first-pass contract package with provisional extension points for later ratification.
