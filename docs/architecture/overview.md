# Ecosystem Architecture Overview

`nexus` sits at the ecosystem contract layer above implementation and consumer repositories.

## Layer model

1. **Contract Layer (`nexus`)**
   - defines profile contracts
   - defines shared schemas and compatibility semantics
   - publishes governance and lifecycle policy
2. **Implementation Layers (Nexbus, NexCore_*)**
   - implement transport and firmware behavior
   - must align to contract declarations from `nexus`
3. **Consumer Layer (NexSight and other clients/tooling)**
   - consume declared contract surfaces
   - rely on compatibility and stability guarantees from `nexus`

## Core architectural rule

`nexus` defines the contract.
Implementations and consumers align to that contract.
`nexus` does not derive authoritative contract behavior from implementation quirks.

## Initial scope

The first profile package in this repo is `nc1`, currently scaffolded for contract migration and iterative refinement.
