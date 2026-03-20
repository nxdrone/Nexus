.PHONY: validate validate-nc1 drift-sample drift-real manifest-real

validate: validate-nc1

validate-nc1:
	python tools/validate/contracts/validate_contracts.py --profile nc1

manifest-real:
	python tools/drift/validate_manifest_against_schema.py --manifest tools/drift/examples/nc1_real_impl_manifest.json

drift-sample:
	python tools/drift/compare_manifest_to_contract.py --manifest tools/drift/examples/sample_nc1_impl_manifest.json --allow-drift

drift-real:
	python tools/drift/compare_manifest_to_contract.py --manifest tools/drift/examples/nc1_real_impl_manifest.json
