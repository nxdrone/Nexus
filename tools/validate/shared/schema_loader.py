"""Schema loading and lightweight validation helpers for Nexus contract tooling.

Implements a focused subset of JSON Schema rules used by this repository:
- type
- required
- enum
- properties
- items
- additionalProperties=false
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Tuple

from reporting import Issue


TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "number": (int, float),
    "integer": int,
}


def load_schema(path: Path) -> Tuple[dict[str, Any] | None, list[Issue]]:
    issues: list[Issue] = []
    if not path.exists():
        issues.append(Issue("error", "schema", str(path), "Schema file does not exist."))
        return None, issues

    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(
            Issue(
                "error",
                "schema",
                str(path),
                f"Schema JSON invalid at line {exc.lineno}, column {exc.colno}: {exc.msg}",
            )
        )
        return None, issues

    return schema, issues


def _validate_instance(instance: Any, schema: dict[str, Any], path: str) -> list[str]:
    problems: list[str] = []

    expected_type = schema.get("type")
    if expected_type:
        py_type = TYPE_MAP.get(expected_type)
        if py_type and not isinstance(instance, py_type):
            problems.append(f"{path}: expected type '{expected_type}', found '{type(instance).__name__}'")
            return problems

    enum_values = schema.get("enum")
    if enum_values is not None and instance not in enum_values:
        problems.append(f"{path}: value '{instance}' not in enum {enum_values}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                problems.append(f"{path}: missing required property '{key}'")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    problems.append(f"{path}: additional property '{key}' is not allowed")

        for key, value in instance.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                problems.extend(_validate_instance(value, child_schema, f"{path}/{key}"))

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                problems.extend(_validate_instance(item, item_schema, f"{path}/{idx}"))

    return problems


def validate_json(instance: Any, schema: dict[str, Any], path: str) -> list[Issue]:
    return [Issue("error", "schema", path, problem) for problem in _validate_instance(instance, schema, "#")]


def validate_many(
    tasks: Iterable[tuple[Any, Path, str]],
) -> list[Issue]:
    issues: list[Issue] = []
    for instance, schema_path, display_path in tasks:
        schema, schema_issues = load_schema(schema_path)
        issues.extend(schema_issues)
        if schema is None:
            continue
        issues.extend(validate_json(instance, schema, display_path))
    return issues
