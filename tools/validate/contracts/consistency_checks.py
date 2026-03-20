"""Internal consistency checks for NC1 contract artifacts.

These checks validate relationships between authoritative contract files.
They do not infer or rewrite contract definitions from implementation behavior.
"""

from __future__ import annotations

from typing import Iterable, List

from reporting import Issue

STABILITY_CLASSES = {"required", "optional", "extension", "experimental"}

CANONICAL_STATE_PRESENTATION = {
    "safe": {"color_name": "blue", "pattern_intent": "twinkle"},
    "armed": {"color_name": "red", "pattern_intent": "solid"},
    "test_mode": {"color_name": "yellow", "pattern_intent": "blink"},
    "failsafe": {"color_name": "purple", "pattern_intent": "solid"},
    "signal_loss": {"color_name": "white", "pattern_intent": "blink"},
}


def _collect_duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def run_consistency_checks(bundle: dict[str, dict]) -> List[Issue]:
    issues: List[Issue] = []

    capabilities = bundle.get("capabilities", {})
    commands = bundle.get("commands", {})
    config = bundle.get("config", {})
    compatibility = bundle.get("compatibility", {})
    profile = bundle.get("profile", {})

    capability_entries = capabilities.get("capabilities", [])
    capability_ids = [entry.get("id", "") for entry in capability_entries if isinstance(entry, dict)]

    for duplicate in sorted(_collect_duplicates(capability_ids)):
        issues.append(Issue("error", "consistency", "capabilities.json", f"Duplicate capability id: {duplicate}"))

    command_entries = commands.get("commands", [])
    command_tokens = [entry.get("token", "") for entry in command_entries if isinstance(entry, dict)]

    for duplicate in sorted(_collect_duplicates(command_tokens)):
        issues.append(Issue("error", "consistency", "commands.json", f"Duplicate command token: {duplicate}"))

    command_categories = {
        entry.get("category")
        for entry in command_entries
        if isinstance(entry, dict) and isinstance(entry.get("category"), str)
    }
    for category in sorted(command_categories):
        if category != category.strip() or " " in category:
            issues.append(
                Issue(
                    "error",
                    "consistency",
                    "commands.json",
                    f"Invalid command category '{category}' (use snake_case-like tokens).",
                )
            )

    for idx, entry in enumerate(command_entries):
        if not isinstance(entry, dict):
            issues.append(Issue("error", "consistency", "commands.json", f"commands[{idx}] must be an object."))
            continue

        for required in [
            "token",
            "display_name",
            "stability_class",
            "category",
            "purpose",
            "response_contract",
            "completion_model",
            "error_behavior",
        ]:
            if required not in entry:
                issues.append(
                    Issue("error", "consistency", "commands.json", f"{entry.get('token', f'commands[{idx}]')} missing required field '{required}'.")
                )

        stability = entry.get("stability_class")
        if stability not in STABILITY_CLASSES:
            issues.append(
                Issue(
                    "error",
                    "consistency",
                    "commands.json",
                    f"{entry.get('token', f'commands[{idx}]')} has unknown stability_class '{stability}'.",
                )
            )

    for idx, entry in enumerate(capability_entries):
        if not isinstance(entry, dict):
            issues.append(Issue("error", "consistency", "capabilities.json", f"capabilities[{idx}] must be an object."))
            continue

        stability = entry.get("stability_class")
        if stability not in STABILITY_CLASSES:
            issues.append(
                Issue(
                    "error",
                    "consistency",
                    "capabilities.json",
                    f"{entry.get('id', f'capabilities[{idx}]')} has unknown stability_class '{stability}'.",
                )
            )

        for token in entry.get("related_commands", []):
            if token not in command_tokens:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "capabilities.json",
                        f"{entry.get('id')} references unknown command token '{token}'.",
                    )
                )

    config_group_ids = [
        group.get("id") for group in config.get("groups", []) if isinstance(group, dict)
    ]
    for duplicate in sorted(_collect_duplicates([g for g in config_group_ids if isinstance(g, str)])):
        issues.append(Issue("error", "consistency", "config.schema.json", f"Duplicate config group id: {duplicate}"))

    state_machine = bundle.get("state_machine", {})
    state_presentation = bundle.get("state_presentation", {})

    if state_presentation:
        presentation_entries = state_presentation.get("state_presentations", [])
        presentation_ids = [entry.get("state_id") for entry in presentation_entries if isinstance(entry, dict)]

        for duplicate in sorted(_collect_duplicates([s for s in presentation_ids if isinstance(s, str)])):
            issues.append(Issue("error", "consistency", "state-presentation.json", f"Duplicate state presentation state_id: {duplicate}"))

        state_ids = [
            state.get("id") for state in state_machine.get("states", []) if isinstance(state, dict)
        ]

        for state_id in state_ids:
            if state_id not in presentation_ids:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        f"Missing state presentation entry for state-machine state '{state_id}'.",
                    )
                )

        presentation_map = {
            entry.get("state_id"): entry
            for entry in presentation_entries
            if isinstance(entry, dict) and isinstance(entry.get("state_id"), str)
        }

        for state_id, expected in CANONICAL_STATE_PRESENTATION.items():
            actual = presentation_map.get(state_id)
            if not actual:
                continue
            if actual.get("color_name") != expected["color_name"]:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        f"State '{state_id}' color_name must be '{expected['color_name']}' (found '{actual.get('color_name')}').",
                    )
                )
            if actual.get("pattern_intent") != expected["pattern_intent"]:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        f"State '{state_id}' pattern_intent must be '{expected['pattern_intent']}' (found '{actual.get('pattern_intent')}').",
                    )
                )

        combined_entries = state_presentation.get("combined_state_presentations", [])
        armed_test = next((entry for entry in combined_entries if isinstance(entry, dict) and entry.get("state_id") == "armed+test_mode"), None)
        if not armed_test:
            issues.append(Issue("error", "consistency", "state-presentation.json", "Missing combined state presentation for 'armed+test_mode'."))
        else:
            if armed_test.get("primary_color_name") != "red":
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        "Combined state 'armed+test_mode' primary_color_name must be 'red'.",
                    )
                )
            allowed = armed_test.get("allowed_pattern_intents", [])
            if not isinstance(allowed, list) or "blink" not in allowed or "alternate" not in allowed:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        "Combined state 'armed+test_mode' must allow both 'blink' and 'alternate' pattern intents.",
                    )
                )

    commissioning = bundle.get("commissioning", {})
    for stage in commissioning.get("stages", []):
        if not isinstance(stage, dict):
            continue
        for editable_group in stage.get("editable_groups", []):
            if editable_group not in config_group_ids:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "commissioning.schema.json",
                        f"Stage '{stage.get('id')}' references unknown config group '{editable_group}'.",
                    )
                )

    required_caps = compatibility.get("required_capabilities", [])
    for cap_id in required_caps:
        if cap_id not in capability_ids:
            issues.append(
                Issue(
                    "error",
                    "consistency",
                    "compatibility.json",
                    f"required_capabilities contains unknown capability id '{cap_id}'.",
                )
            )

    required_command_behaviors = compatibility.get("required_command_behaviors", [])
    for behavior in required_command_behaviors:
        if not isinstance(behavior, dict):
            continue
        token = behavior.get("token")
        if token not in command_tokens:
            issues.append(
                Issue(
                    "error",
                    "consistency",
                    "compatibility.json",
                    f"required_command_behaviors references unknown command token '{token}'.",
                )
            )

    profile_id = profile.get("id")
    for field_name in ["profile_id"]:
        config_groups = config.get("groups", [])
        if config_groups:
            platform_group = next((g for g in config_groups if isinstance(g, dict) and g.get("id") == "platform"), None)
            if isinstance(platform_group, dict):
                platform_profile_id = platform_group.get("example_fields", {}).get(field_name)
                if profile_id and platform_profile_id and platform_profile_id != profile_id:
                    issues.append(
                        Issue(
                            "error",
                            "consistency",
                            "config.schema.json",
                            f"platform.example_fields.{field_name} ('{platform_profile_id}') does not match profile id '{profile_id}'.",
                        )
                    )

    if profile.get("status") == "provisional":
        issues.append(
            Issue(
                "warning",
                "consistency",
                "profile.json",
                "Profile status is provisional; consumers should avoid hard dependencies on extension/experimental surfaces.",
            )
        )

    return issues
