# Drift Report (Sample)

Manifest: `tools/drift/examples/sample_nc1_impl_manifest.json`

## Errors
- ❌ Required capability not supported=true: testing.catalog_discovery
- ❌ Missing required command: commissioning.apply_stage
- ❌ Missing required command: safety.stop_all

## Warnings
- ⚠️ Unknown capability declared by implementation: vendor.custom_capability
- ⚠️ Unknown command declared by implementation: vendor.custom_command
- ⚠️ Stability mismatch for test.list_catalog: manifest=optional contract=required
- ⚠️ Config groups absent from implementation manifest: commissioning, platform, topology
- ⚠️ Unknown config groups in implementation manifest: vendor_group

Authority note: this report compares implementation declarations against Nexus contract artifacts and does not redefine contract authority.
