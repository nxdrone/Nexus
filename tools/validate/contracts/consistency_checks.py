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

        seen_priorities = {}
        for entry in presentation_entries:
            if not isinstance(entry, dict):
                continue
            state_id = entry.get("state_id")
            priority = entry.get("priority")
            if isinstance(priority, int):
                if priority in seen_priorities:
                    issues.append(
                        Issue(
                            "error",
                            "consistency",
                            "state-presentation.json",
                            f"Priority {priority} is reused by '{seen_priorities[priority]}' and '{state_id}'.",
                        )
                    )
                else:
                    seen_priorities[priority] = state_id

        expected_safety_levels = {
            "safe": "safe",
            "test_mode": "caution",
            "armed": "hazard",
            "failsafe": "fault",
            "signal_loss": "unknown",
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
            expected_level = expected_safety_levels.get(state_id)
            if expected_level and actual.get("safety_level") != expected_level:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        f"State '{state_id}' safety_level must be '{expected_level}' (found '{actual.get('safety_level')}').",
                    )
                )

        failsafe = presentation_map.get("failsafe")
        if not failsafe:
            issues.append(Issue("error", "consistency", "state-presentation.json", "Missing FAILSAFE state presentation."))
        else:
            failsafe_priority = failsafe.get("priority")
            if not isinstance(failsafe_priority, int):
                issues.append(Issue("error", "consistency", "state-presentation.json", "FAILSAFE must declare integer priority."))
            else:
                for entry in presentation_entries:
                    if not isinstance(entry, dict) or entry.get("state_id") == "failsafe":
                        continue
                    priority = entry.get("priority")
                    if isinstance(priority, int) and priority >= failsafe_priority:
                        issues.append(
                            Issue(
                                "error",
                                "consistency",
                                "state-presentation.json",
                                f"FAILSAFE priority ({failsafe_priority}) must be higher than '{entry.get('state_id')}' ({priority}).",
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
            members = armed_test.get("member_states", [])
            if members != ["armed", "test_mode"]:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        "Combined state 'armed+test_mode' member_states must be ['armed', 'test_mode'].",
                    )
                )
            model = armed_test.get("composition_model", {})
            if not isinstance(model, dict):
                issues.append(Issue("error", "consistency", "state-presentation.json", "Combined state composition_model must be an object."))
            else:
                expected_model = {
                    "primary_state_id": "armed",
                    "pattern_modifier_state_id": "test_mode",
                    "primary_color_source": "armed",
                    "secondary_signal_source": "test_mode",
                }
                for key, value in expected_model.items():
                    if model.get(key) != value:
                        issues.append(
                            Issue(
                                "error",
                                "consistency",
                                "state-presentation.json",
                                f"Combined state 'armed+test_mode' {key} must be '{value}'.",
                            )
                        )

        override_rules = state_presentation.get("override_rules", [])
        failsafe_override = next(
            (
                rule
                for rule in override_rules
                if isinstance(rule, dict) and rule.get("id") == "failsafe_visual_override"
            ),
            None,
        )
        if not failsafe_override:
            issues.append(
                Issue(
                    "error",
                    "consistency",
                    "state-presentation.json",
                    "Missing required override rule 'failsafe_visual_override'.",
                )
            )
        else:
            if failsafe_override.get("state_id") != "failsafe":
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        "failsafe_visual_override must reference state_id 'failsafe'.",
                    )
                )
            dominates = failsafe_override.get("dominates_states", [])
            expected_dominates = {"safe", "armed", "test_mode", "signal_loss", "armed+test_mode"}
            if set(dominates) != expected_dominates:
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        "failsafe_visual_override dominates_states must exactly cover safe, armed, test_mode, signal_loss, and armed+test_mode.",
                    )
                )
            if failsafe_override.get("safety_level") != "fault":
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        "failsafe_visual_override safety_level must be 'fault'.",
                    )
                )

            if isinstance(failsafe.get("priority"), int) and failsafe_override.get("priority") != failsafe.get("priority"):
                issues.append(
                    Issue(
                        "error",
                        "consistency",
                        "state-presentation.json",
                        "failsafe_visual_override priority must match FAILSAFE state priority.",
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
