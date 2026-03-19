# Drift Report

Manifest: `tools/drift/examples/sample_nc1_impl_manifest.json`

## Contract violations
- ❌ Required capability not supported=true: testing.catalog_discovery
- ❌ Missing required command: commissioning.apply_stage
- ❌ Missing required command: safety.stop_all
- ❌ Missing contract states: test_mode

## Advisory findings
- ⚠️ Extension capability (acceptable): vendor.custom_capability
- ⚠️ Stability mismatch: test.list_catalog manifest=optional contract=required
- ⚠️ Extension command (acceptable): vendor.custom_command
- ⚠️ Missing declared config groups in manifest: commissioning, platform, topology
- ⚠️ Extension config groups (acceptable): vendor_group

Authority note: this report compares implementation declarations against Nexus contract artifacts and does not redefine contract authority.
