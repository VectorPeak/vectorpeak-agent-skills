#!/usr/bin/env python3
"""Validate contract review JSON without requiring external packages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CONTRACT_TYPES = {"lease", "nda", "employment", "freelance", "saas_tos", "loan", "purchase", "other", "unknown"}
GRADES = {"A+", "A", "B+", "B", "C+", "C", "D", "F"}
ISSUE_SEVERITIES = {"red", "yellow"}
REQUIRED_TOP_LEVEL = [
    "contract_type",
    "summary",
    "parties",
    "key_terms",
    "red_flags",
    "warnings",
    "protections",
    "missing_protections",
    "fairness_score",
    "fairness_grade",
    "negotiation_points",
    "lawyer_recommended",
    "disclaimer",
]
ISSUE_FIELDS = ["title", "severity", "clause", "quote", "explanation", "suggestion"]
PROTECTION_FIELDS = ["title", "clause", "quote", "explanation"]


def fail(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def expect_string(errors: list[str], data: dict[str, Any], key: str, path: str, allow_empty: bool = False) -> None:
    value = data.get(key)
    if not isinstance(value, str):
        fail(errors, path, "must be a string")
    elif not allow_empty and not value.strip():
        fail(errors, path, "must not be empty")


def expect_string_list(errors: list[str], data: dict[str, Any], key: str, path: str) -> None:
    value = data.get(key)
    if not isinstance(value, list):
        fail(errors, path, "must be an array")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str):
            fail(errors, f"{path}[{index}]", "must be a string")


def validate_issue(errors: list[str], item: Any, path: str, expected_severity: str) -> None:
    if not isinstance(item, dict):
        fail(errors, path, "must be an object")
        return
    for key in ISSUE_FIELDS:
        if key not in item:
            fail(errors, f"{path}.{key}", "is required")
    expect_string(errors, item, "title", f"{path}.title")
    expect_string(errors, item, "clause", f"{path}.clause")
    expect_string(errors, item, "quote", f"{path}.quote", allow_empty=True)
    expect_string(errors, item, "explanation", f"{path}.explanation")
    expect_string(errors, item, "suggestion", f"{path}.suggestion")
    severity = item.get("severity")
    if severity not in ISSUE_SEVERITIES:
        fail(errors, f"{path}.severity", f"must be one of {sorted(ISSUE_SEVERITIES)}")
    elif severity != expected_severity:
        fail(errors, f"{path}.severity", f"must be {expected_severity!r}")


def validate_protection(errors: list[str], item: Any, path: str) -> None:
    if not isinstance(item, dict):
        fail(errors, path, "must be an object")
        return
    for key in PROTECTION_FIELDS:
        if key not in item:
            fail(errors, f"{path}.{key}", "is required")
    expect_string(errors, item, "title", f"{path}.title")
    expect_string(errors, item, "clause", f"{path}.clause")
    expect_string(errors, item, "quote", f"{path}.quote", allow_empty=True)
    expect_string(errors, item, "explanation", f"{path}.explanation")


def validate_review(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["$: must be a JSON object"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            fail(errors, f"$.{key}", "is required")

    if data.get("contract_type") not in CONTRACT_TYPES:
        fail(errors, "$.contract_type", f"must be one of {sorted(CONTRACT_TYPES)}")
    expect_string(errors, data, "summary", "$.summary")
    expect_string_list(errors, data, "parties", "$.parties")
    expect_string_list(errors, data, "key_terms", "$.key_terms")
    expect_string_list(errors, data, "missing_protections", "$.missing_protections")
    expect_string_list(errors, data, "negotiation_points", "$.negotiation_points")

    score = data.get("fairness_score")
    if not isinstance(score, int) or isinstance(score, bool):
        fail(errors, "$.fairness_score", "must be an integer")
    elif not 0 <= score <= 100:
        fail(errors, "$.fairness_score", "must be between 0 and 100")

    if data.get("fairness_grade") not in GRADES:
        fail(errors, "$.fairness_grade", f"must be one of {sorted(GRADES)}")
    if not isinstance(data.get("lawyer_recommended"), bool):
        fail(errors, "$.lawyer_recommended", "must be a boolean")
    expect_string(errors, data, "disclaimer", "$.disclaimer")

    for key, severity in (("red_flags", "red"), ("warnings", "yellow")):
        value = data.get(key)
        if not isinstance(value, list):
            fail(errors, f"$.{key}", "must be an array")
            continue
        for index, item in enumerate(value):
            validate_issue(errors, item, f"$.{key}[{index}]", severity)

    protections = data.get("protections")
    if not isinstance(protections, list):
        fail(errors, "$.protections", "must be an array")
    else:
        for index, item in enumerate(protections):
            validate_protection(errors, item, f"$.protections[{index}]")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Review JSON file path.")
    args = parser.parse_args()

    path = Path(args.input)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    errors = validate_review(data)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("VALID")


if __name__ == "__main__":
    main()
