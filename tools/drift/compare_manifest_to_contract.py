#!/usr/bin/env python3
"""Compare implementation manifest surfaces to authoritative NC1 contract artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_manifest_shape(manifest: dict) -> list[str]:
    errors: list[str] = []

    for key in ["id", "profile", "implementation", "capabilities", "commands"]:
        if key not in manifest:
            errors.append(f"Missing required top-level key '{key}'")

    profile = manifest.get("profile", {})
    if not isinstance(profile, dict) or "id" not in profile or "version" not in profile:
        errors.append("profile must include id and version")

    implementation = manifest.get("implementation", {})
    if not isinstance(implementation, dict) or "name" not in implementation or "type" not in implementation:
        errors.append("implementation must include name and type")

    capabilities = manifest.get("capabilities", [])
    if not isinstance(capabilities, list):
        errors.append("capabilities must be an array")
    else:
        for idx, capability in enumerate(capabilities):
            if not isinstance(capability, dict):
                errors.append(f"capabilities[{idx}] must be an object")
                continue
            if "id" not in capability or "supported" not in capability:
                errors.append(f"capabilities[{idx}] must include id and supported")

    commands = manifest.get("commands", [])
    if not isinstance(commands, list):
        errors.append("commands must be an array")
    else:
        for idx, command in enumerate(commands):
            if not isinstance(command, dict) or "token" not in command:
                errors.append(f"commands[{idx}] must include token")

    return errors


def collect_contract_surfaces(contract_root: Path) -> dict:
    profile = load_json(contract_root / "profile.json")
    capabilities = load_json(contract_root / "capabilities.json")
    commands = load_json(contract_root / "commands.json")
    config = load_json(contract_root / "config.schema.json")

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

    return {
        "profile_id": profile.get("id"),
        "profile_version": profile.get("version"),
        "required_capabilities": required_capabilities,
        "known_capabilities": known_capabilities,
        "required_commands": required_commands,
        "known_commands": known_commands,
        "config_groups": config_groups,
    }


def compare(manifest: dict, contract: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    manifest_profile = manifest.get("profile", {})
    if manifest_profile.get("id") != contract["profile_id"]:
        errors.append(
            f"Profile id mismatch: manifest={manifest_profile.get('id')} contract={contract['profile_id']}"
        )

    if manifest_profile.get("version") != contract["profile_version"]:
        warnings.append(
            f"Profile version mismatch: manifest={manifest_profile.get('version')} contract={contract['profile_version']}"
        )

    manifest_caps = {item.get("id"): item for item in manifest.get("capabilities", []) if isinstance(item, dict)}
    manifest_commands = {item.get("token"): item for item in manifest.get("commands", []) if isinstance(item, dict)}
    manifest_groups = set(manifest.get("config_groups", []))

    for required_cap in sorted(contract["required_capabilities"]):
        if required_cap not in manifest_caps:
            errors.append(f"Missing required capability: {required_cap}")
        elif manifest_caps[required_cap].get("supported") is not True:
            errors.append(f"Required capability not supported=true: {required_cap}")

    for cap_id in sorted(manifest_caps):
        if cap_id not in contract["known_capabilities"]:
            warnings.append(f"Unknown capability declared by implementation: {cap_id}")

    for required_cmd in sorted(contract["required_commands"]):
        if required_cmd not in manifest_commands:
            errors.append(f"Missing required command: {required_cmd}")

    for token, command in manifest_commands.items():
        if token not in contract["known_commands"]:
            warnings.append(f"Unknown command declared by implementation: {token}")
            continue
        contract_stability = contract["known_commands"][token].get("stability_class")
        manifest_stability = command.get("stability_class")
        if manifest_stability and manifest_stability != contract_stability:
            warnings.append(
                f"Stability mismatch for {token}: manifest={manifest_stability} contract={contract_stability}"
            )

    missing_groups = contract["config_groups"] - manifest_groups
    if missing_groups:
        warnings.append(
            f"Config groups absent from implementation manifest: {', '.join(sorted(missing_groups))}"
        )

    unknown_groups = manifest_groups - contract["config_groups"]
    if unknown_groups:
        warnings.append(
            f"Unknown config groups in implementation manifest: {', '.join(sorted(unknown_groups))}"
        )

    return errors, warnings


def render_report(manifest_path: Path, errors: list[str], warnings: list[str]) -> str:
    lines = ["# Drift Report", "", f"Manifest: `{manifest_path}`", ""]

    lines.append("## Errors")
    if errors:
        lines.extend(f"- ❌ {item}" for item in errors)
    else:
        lines.append("- ✅ None")

    lines.append("")
    lines.append("## Warnings")
    if warnings:
        lines.extend(f"- ⚠️ {item}" for item in warnings)
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
    manifest_shape_errors = validate_manifest_shape(manifest)
    if manifest_shape_errors:
        for err in manifest_shape_errors:
            print(f"❌ [schema-lite] {args.manifest}: {err}")
        return 2

    contract = collect_contract_surfaces(args.contract_root)
    errors, warnings = compare(manifest, contract)
    report = render_report(args.manifest, errors, warnings)

    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)

    if errors and not args.allow_drift:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
