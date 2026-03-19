# Source-of-Truth Policy

## Policy statement

Nexus is the authoritative source of truth for ecosystem contracts.

## Required rules

- If a client, tool, or implementation depends on behavior, that behavior must be explicitly declared in Nexus.
- Implementation behavior does not automatically define contract.
- Experimental implementation features must not silently become stable contract surface.
- Contract authority is versioned and auditable through this repository.

## Enforcement intent

Validation/compliance/drift workflows compare implementations and consumers against Nexus artifacts, not the reverse.
