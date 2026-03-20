"""File loading and JSON parsing helpers for Nexus validation tooling."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

from reporting import Issue


NC1_CONTRACT_DIR = Path("contracts/profiles/nc1")


def discover_nc1_contract_files() -> Dict[str, Path]:
    return {
        "profile": NC1_CONTRACT_DIR / "profile.json",
        "capabilities": NC1_CONTRACT_DIR / "capabilities.json",
        "commands": NC1_CONTRACT_DIR / "commands.json",
        "config": NC1_CONTRACT_DIR / "config.schema.json",
        "commissioning": NC1_CONTRACT_DIR / "commissioning.schema.json",
        "state_machine": NC1_CONTRACT_DIR / "state-machine.json",
        "state_presentation": NC1_CONTRACT_DIR / "state-presentation.json",
        "test": NC1_CONTRACT_DIR / "test.schema.json",
        "compatibility": NC1_CONTRACT_DIR / "compatibility.json",
    }


def load_json_file(path: Path) -> Tuple[dict | None, list[Issue]]:
    issues: list[Issue] = []
    if not path.exists():
        issues.append(Issue("error", "loader", str(path), "File does not exist."))
        return None, issues

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(
            Issue(
                "error",
                "loader",
                str(path),
                f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
            )
        )
        return None, issues

    if not isinstance(data, dict):
        issues.append(
            Issue("error", "loader", str(path), "Top-level JSON value must be an object.")
        )
        return None, issues

    return data, issues


def load_contract_bundle() -> Tuple[dict[str, dict], list[Issue]]:
    bundle: dict[str, dict] = {}
    issues: list[Issue] = []

    for key, path in discover_nc1_contract_files().items():
        payload, file_issues = load_json_file(path)
        issues.extend(file_issues)
        if payload is not None:
            bundle[key] = payload

    return bundle, issues
