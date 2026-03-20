#!/usr/bin/env python3
"""Validate Nexus contract artifacts for JSON, schema, and consistency integrity."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
SHARED_DIR = CURRENT_DIR.parent / "shared"
sys.path.insert(0, str(SHARED_DIR))
sys.path.insert(0, str(CURRENT_DIR))

from consistency_checks import run_consistency_checks
from file_loader import discover_nc1_contract_files, load_contract_bundle
from reporting import Report
from schema_loader import validate_many


def build_schema_tasks(bundle: dict[str, dict]) -> list[tuple[object, Path, str]]:
    root = Path(".")
    tasks: list[tuple[object, Path, str]] = []

    if "profile" in bundle:
        tasks.append((bundle["profile"], root / "schemas/profile.schema.json", "contracts/profiles/nc1/profile.json"))

    if "capabilities" in bundle:
        for idx, capability in enumerate(bundle["capabilities"].get("capabilities", [])):
            tasks.append(
                (
                    capability,
                    root / "schemas/capability.schema.json",
                    f"contracts/profiles/nc1/capabilities.json#/capabilities/{idx}",
                )
            )

    if "commands" in bundle:
        for idx, command in enumerate(bundle["commands"].get("commands", [])):
            tasks.append(
                (
                    command,
                    root / "schemas/command.schema.json",
                    f"contracts/profiles/nc1/commands.json#/commands/{idx}",
                )
            )

    if "config" in bundle:
        for idx, group in enumerate(bundle["config"].get("groups", [])):
            tasks.append(
                (
                    group,
                    root / "schemas/config-group.schema.json",
                    f"contracts/profiles/nc1/config.schema.json#/groups/{idx}",
                )
            )


    if "state_presentation" in bundle:
        for idx, entry in enumerate(bundle["state_presentation"].get("state_presentations", [])):
            tasks.append(
                (
                    entry,
                    root / "schemas/state-presentation.schema.json",
                    f"contracts/profiles/nc1/state-presentation.json#/state_presentations/{idx}",
                )
            )

        for idx, entry in enumerate(bundle["state_presentation"].get("combined_state_presentations", [])):
            tasks.append(
                (
                    entry,
                    root / "schemas/combined-state-presentation.schema.json",
                    f"contracts/profiles/nc1/state-presentation.json#/combined_state_presentations/{idx}",
                )
            )

    if "commissioning" in bundle:
        for idx, stage in enumerate(bundle["commissioning"].get("stages", [])):
            stage_instance = {
                "id": stage.get("id"),
                "name": stage.get("display_name"),
                "required": stage.get("required"),
            }
            tasks.append(
                (
                    stage_instance,
                    root / "schemas/commissioning.schema.json",
                    f"contracts/profiles/nc1/commissioning.schema.json#/stages/{idx}",
                )
            )

    return tasks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate NC1 contract artifacts.")
    parser.add_argument(
        "--profile",
        default="nc1",
        help="Profile identifier to validate (currently only nc1 is implemented).",
    )
    args = parser.parse_args()

    report = Report()

    if args.profile != "nc1":
        report.add_error("loader", args.profile, "Only 'nc1' profile is currently supported.")
        print(report.render())
        return 2

    contract_files = discover_nc1_contract_files()
    for _, path in contract_files.items():
        if not path.exists():
            report.add_error("loader", str(path), "Missing required contract file.")

    bundle, load_issues = load_contract_bundle()
    report.extend(load_issues)

    schema_tasks = build_schema_tasks(bundle)
    report.extend(validate_many(schema_tasks))

    report.extend(run_consistency_checks(bundle))

    print(report.render())
    return 1 if report.has_errors() else 0


if __name__ == "__main__":
    raise SystemExit(main())
