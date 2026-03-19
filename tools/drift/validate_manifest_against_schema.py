#!/usr/bin/env python3
"""Validate an implementation manifest against tools/drift/implementation_manifest.schema.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
VALIDATE_SHARED = CURRENT_DIR.parent / "validate" / "shared"
sys.path.insert(0, str(VALIDATE_SHARED))

from schema_loader import load_schema, validate_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate implementation manifest shape.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("tools/drift/implementation_manifest.schema.json"),
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    schema, schema_issues = load_schema(args.schema)
    if schema_issues:
        for issue in schema_issues:
            print(f"❌ [{issue.category}] {issue.path}: {issue.message}")
        return 2

    issues = validate_json(manifest, schema, str(args.manifest))
    if issues:
        for issue in issues:
            print(f"❌ [{issue.category}] {issue.path}: {issue.message}")
        return 1

    print("✅ Manifest validates against implementation manifest schema.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
