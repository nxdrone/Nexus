.PHONY: validate validate-nc1 drift-sample

validate: validate-nc1

validate-nc1:
	python tools/validate/contracts/validate_contracts.py --profile nc1

drift-sample:
	python tools/drift/compare_manifest_to_contract.py --manifest tools/drift/examples/sample_nc1_impl_manifest.json --allow-drift
