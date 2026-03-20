#!/usr/bin/env python3
"""Compare implementation manifest surfaces to authoritative NC1 contract artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
VALIDATE_SHARED = CURRENT_DIR.parent / "validate" / "shared"
sys.path.insert(0, str(VALIDATE_SHARED))

from schema_loader import load_schema, validate_json


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_manifest(manifest: dict) -> dict:
    profile_id = manifest.get("declared_profile_id") or manifest.get("profile", {}).get("id")
    profile_version = manifest.get("declared_profile_version") or manifest.get("profile", {}).get("version")

    config_groups = []
    if isinstance(manifest.get("config_model"), dict):
        for group in manifest["config_model"].get("groups", []):
            if isinstance(group, dict) and "id" in group:
                config_groups.append(group["id"])
    elif isinstance(manifest.get("config_groups"), list):
        config_groups = list(manifest.get("config_groups", []))

    state_ids = []
    if isinstance(manifest.get("state_model"), dict):
        state_ids = list(manifest["state_model"].get("states", []))

    return {
        "profile_id": profile_id,
        "profile_version": profile_version,
        "capabilities": manifest.get("capabilities", []),
        "commands": manifest.get("commands", []),
        "config_groups": config_groups,
        "state_ids": state_ids,
        "authority": manifest.get("exposure", {}).get("authority", {}),
    }


def collect_contract_surfaces(contract_root: Path) -> dict:
    profile = load_json(contract_root / "profile.json")
    capabilities = load_json(contract_root / "capabilities.json")
    commands = load_json(contract_root / "commands.json")
    config = load_json(contract_root / "config.schema.json")
    state_machine = load_json(contract_root / "state-machine.json")

    required_capabilities = {
        item["id"]
        for item in capabilities.get("capabilities", [])
        if item.get("stability_class") == "required"
    }
    known_capabilities = {item["id"]: item for item in capabilities.get("capabilities", [])}

    required_commands = {
        item["token"]
        for item in commands.get("commands", [])
        if item.get("stability_class") == "required"
    }
    known_commands = {item["token"]: item for item in commands.get("commands", [])}

    config_groups = {
        group["id"]
        for group in config.get("groups", [])
        if isinstance(group, dict) and "id" in group
    }

    state_ids = {
        state["id"]
        for state in state_machine.get("states", [])
        if isinstance(state, dict) and "id" in state
    }

    return {
        "profile_id": profile.get("id"),
        "profile_version": profile.get("version"),
        "required_capabilities": required_capabilities,
        "known_capabilities": known_capabilities,
        "required_commands": required_commands,
        "known_commands": known_commands,
        "config_groups": config_groups,
        "state_ids": state_ids,
    }


def compare(manifest: dict, contract: dict) -> tuple[list[str], list[str]]:
    violations: list[str] = []
    advisories: list[str] = []

    if manifest["profile_id"] != contract["profile_id"]:
        violations.append(
            f"Profile id mismatch: manifest={manifest['profile_id']} contract={contract['profile_id']}"
        )

    if manifest["profile_version"] != contract["profile_version"]:
        advisories.append(
            f"Contract version mismatch: manifest={manifest['profile_version']} contract={contract['profile_version']}"
        )

    authority = manifest["authority"]
    if authority.get("contract_source") != "nexus":
        violations.append("Authority mismatch: exposure.authority.contract_source must be 'nexus'.")
    if authority.get("firmware_role") != "declaration_only":
        violations.append("Authority mismatch: exposure.authority.firmware_role must be 'declaration_only'.")

    manifest_caps = {item.get("id"): item for item in manifest["capabilities"] if isinstance(item, dict)}
    manifest_commands = {item.get("token"): item for item in manifest["commands"] if isinstance(item, dict)}
    manifest_groups = set(manifest["config_groups"])
    manifest_states = set(manifest["state_ids"])

    for required_cap in sorted(contract["required_capabilities"]):
        if required_cap not in manifest_caps:
            violations.append(f"Missing required capability: {required_cap}")
        elif manifest_caps[required_cap].get("supported") is not True:
            violations.append(f"Required capability not supported=true: {required_cap}")

    for cap_id in sorted(manifest_caps):
        if cap_id not in contract["known_capabilities"]:
            advisories.append(f"Extension capability (acceptable): {cap_id}")

    for required_cmd in sorted(contract["required_commands"]):
        if required_cmd not in manifest_commands:
            violations.append(f"Missing required command: {required_cmd}")

    for token, command in manifest_commands.items():
        if token not in contract["known_commands"]:
            advisories.append(f"Extension command (acceptable): {token}")
            continue
        contract_stability = contract["known_commands"][token].get("stability_class")
        manifest_stability = command.get("stability_class")
        if manifest_stability and manifest_stability != contract_stability:
            advisories.append(
                f"Stability mismatch: {token} manifest={manifest_stability} contract={contract_stability}"
            )

    missing_groups = contract["config_groups"] - manifest_groups
    if missing_groups:
        advisories.append(
            f"Missing declared config groups in manifest: {', '.join(sorted(missing_groups))}"
        )

    unknown_groups = manifest_groups - contract["config_groups"]
    if unknown_groups:
        advisories.append(
            f"Extension config groups (acceptable): {', '.join(sorted(unknown_groups))}"
        )

    missing_states = contract["state_ids"] - manifest_states
    if missing_states:
        violations.append(
            f"Missing contract states: {', '.join(sorted(missing_states))}"
        )

    unknown_states = manifest_states - contract["state_ids"]
    if unknown_states:
        advisories.append(
            f"Extension states (acceptable if documented): {', '.join(sorted(unknown_states))}"
        )

    for token, command in manifest_commands.items():
        if token in contract["known_commands"] and contract["known_commands"][token].get("stability_class") == "experimental":
            if command.get("stability_class"):
                advisories.append(
                    f"Experimental command flagged: {token} ({command.get('stability_class')})"
                )

    return violations, advisories


def render_report(manifest_path: Path, violations: list[str], advisories: list[str]) -> str:
    lines = ["# Drift Report", "", f"Manifest: `{manifest_path}`", ""]

    lines.append("## Contract violations")
    if violations:
        lines.extend(f"- ❌ {item}" for item in violations)
    else:
        lines.append("- ✅ None")

    lines.append("")
    lines.append("## Advisory findings")
    if advisories:
        lines.extend(f"- ⚠️ {item}" for item in advisories)
    else:
        lines.append("- ✅ None")

    lines.append("")
    lines.append(
        "Authority note: this report compares implementation declarations against Nexus contract artifacts and does not redefine contract authority."
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare implementation manifest to NC1 contract.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--contract-root", type=Path, default=Path("contracts/profiles/nc1"))
    parser.add_argument("--allow-drift", action="store_true", help="Return success even when drift is detected.")
    parser.add_argument("--output", type=Path, help="Optional output file for markdown report.")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    schema_path = Path("tools/drift/implementation_manifest.schema.json")
    schema, schema_load_issues = load_schema(schema_path)
    if schema_load_issues:
        for issue in schema_load_issues:
            print(f"❌ [{issue.category}] {issue.path}: {issue.message}")
        return 2

    schema_issues = validate_json(manifest, schema, str(args.manifest))
    if schema_issues:
        for issue in schema_issues:
            print(f"❌ [{issue.category}] {issue.path}: {issue.message}")
        return 2

    normalized = normalize_manifest(manifest)
    contract = collect_contract_surfaces(args.contract_root)
    violations, advisories = compare(normalized, contract)
    report = render_report(args.manifest, violations, advisories)

    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)

    if violations and not args.allow_drift:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
