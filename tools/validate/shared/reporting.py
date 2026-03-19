"""Reporting helpers for Nexus contract validation.

This module only reports validation and consistency findings.
It does not mutate authoritative contract artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Issue:
    severity: str  # error | warning
    category: str  # schema | consistency | loader
    path: str
    message: str


class Report:
    def __init__(self) -> None:
        self.issues: List[Issue] = []

    def add_error(self, category: str, path: str, message: str) -> None:
        self.issues.append(Issue("error", category, path, message))

    def add_warning(self, category: str, path: str, message: str) -> None:
        self.issues.append(Issue("warning", category, path, message))

    def extend(self, issues: Iterable[Issue]) -> None:
        self.issues.extend(issues)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    def has_errors(self) -> bool:
        return self.error_count > 0

    def render(self) -> str:
        if not self.issues:
            return "✅ Validation passed with no issues."

        lines = []
        for issue in self.issues:
            icon = "❌" if issue.severity == "error" else "⚠️"
            lines.append(f"{icon} [{issue.category}] {issue.path}: {issue.message}")
        lines.append("")
        lines.append(
            f"Summary: {self.error_count} error(s), {self.warning_count} warning(s)."
        )
        return "\n".join(lines)
