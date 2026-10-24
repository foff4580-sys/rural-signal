#!/usr/bin/env python3
"""Fail-closed checks for the private contest-edition review package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import engine


ROOT = Path(__file__).resolve().parent
EXPECTED_RESULTS = {case["id"] for case in engine.load_fixtures()}


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    index = (ROOT / "static/index.html").read_text(encoding="utf-8")
    styles = (ROOT / "static/styles.css").read_text(encoding="utf-8")
    script = (ROOT / "static/app.js").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    submission = (ROOT / "SUBMISSION.md").read_text(encoding="utf-8")

    for path in ("/styles.css", "/app.js"):
        if path not in index:
            fail(f"index is missing {path}")
    if "[hidden]{display:none!important}" not in styles:
        fail("hidden-state CSS protection is missing")
    if re.search(r"https?://", index + styles + script):
        fail("UI contains a remote dependency")
    if "not an emergency service" not in (index + readme + submission).lower():
        fail("emergency-service boundary is missing")
    if "AI-assisted development disclosure" not in submission:
        fail("submission lacks the AI-assisted development disclosure")
    if "/home/" in (index + styles + script + readme + submission):
        fail("public release contains a machine-specific home path")

    fixtures = {case["id"]: case for case in engine.load_fixtures()}
    result_files = {path.stem for path in engine.RESULTS.glob("*.json")}
    if result_files != EXPECTED_RESULTS:
        fail(f"result set mismatch: {sorted(result_files)}")
    for case_id, case in fixtures.items():
        result = json.loads((engine.RESULTS / f"{case_id}.json").read_text(encoding="utf-8"))
        if result.get("case_id") != case_id or not result.get("passed") or result.get("errors"):
            fail(f"{case_id}: saved live result is not a clean pass")
        output = result.get("output", {})
        if engine.validate_output(case, output):
            fail(f"{case_id}: saved result no longer passes the current validator")
        if output.get("source_status") != case["locked"]["source_status"]:
            fail(f"{case_id}: trust status changed")
        if len(output.get("sms", "")) > 160:
            fail(f"{case_id}: SMS exceeds 160 characters")

    print("PASS package structure, disclosure, offline UI, and 4 saved live results")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        sys.exit(1)
