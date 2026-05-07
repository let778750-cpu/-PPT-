"""Check experiment workflow state and artifact consistency.

This script intentionally avoids third-party YAML dependencies so it can run in
the same minimal Python environment used by the experiments.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PATH_LINE = re.compile(r"^\s*path:\s*(.+?)\s*$")
EXISTS_LINE = re.compile(r"^\s*exists:\s*(true|false)\s*$", re.IGNORECASE)
PHASE_STATUS_LINE = re.compile(r"^\s{2}(phase\d+_[^:]+):\s*$")
STATUS_LINE = re.compile(r"^\s{4}status:\s*(.*?)\s*$")
TOP_STATUS_LINE = re.compile(r"^\s{2}status:\s*(.*?)\s*$")
FIELD_LINE = re.compile(
    r"^\s{2,8}(report_tex|report_pdf|pptx_path|svg_pptx_path|brief_path|project_path|data_dir|source_path|raw_data_dir|processed_data_dir):\s*(.+?)\s*$"
)


@dataclass
class Issue:
    level: str
    scope: str
    message: str


def clean_value(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if (value[0], value[-1]) in {('"', '"'), ("'", "'")}:
        return value[1:-1]
    return value


def resolve_existing_path(root: Path, code_dir: Path, raw_path: str) -> Path | None:
    raw_path = clean_value(raw_path)
    if not raw_path:
        return None
    candidate = Path(raw_path)
    candidates = []
    if candidate.is_absolute():
        candidates.append(candidate)
    else:
        candidates.append(root / candidate)
        candidates.append(code_dir / candidate)
    for path in candidates:
        if path.exists():
            return path
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_experiment_id(state_text: str) -> str | None:
    match = re.search(r"^\s{2}experiment_id:\s*(\d+)\s*$", state_text, re.MULTILINE)
    return match.group(1) if match else None


def parse_phase_statuses(state_text: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    current: str | None = None
    for line in state_text.splitlines():
        phase_match = PHASE_STATUS_LINE.match(line)
        if phase_match:
            current = phase_match.group(1)
            continue
        status_match = STATUS_LINE.match(line)
        if current and status_match:
            statuses[current] = clean_value(status_match.group(1))
            current = None
    return statuses


def parse_top_experiment_status(state_text: str) -> str | None:
    in_experiment = False
    for line in state_text.splitlines():
        if line.startswith("experiment:"):
            in_experiment = True
            continue
        if in_experiment and line and not line.startswith(" "):
            break
        if in_experiment:
            match = TOP_STATUS_LINE.match(line)
            if match:
                return clean_value(match.group(1))
    return None


def parse_output_paths(state_text: str) -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    for line in state_text.splitlines():
        match = FIELD_LINE.match(line)
        if match:
            paths.append((match.group(1), clean_value(match.group(2))))
    return paths


def parse_manifest_paths(manifest_text: str) -> list[tuple[str, bool]]:
    paths: list[tuple[str, bool]] = []
    current_path: str | None = None
    for line in manifest_text.splitlines():
        path_match = PATH_LINE.match(line)
        if path_match:
            current_path = clean_value(path_match.group(1))
            continue
        exists_match = EXISTS_LINE.match(line)
        if exists_match and current_path:
            paths.append((current_path, exists_match.group(1).lower() == "true"))
            current_path = None
    return paths


def check_workflow(root: Path, workflow_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    code_dir = workflow_dir.parent
    scope = str(code_dir.relative_to(root)) if code_dir.is_relative_to(root) else str(code_dir)

    state_path = workflow_dir / "workflow_state.yaml"
    manifest_path = workflow_dir / "artifacts_manifest.yaml"
    log_path = workflow_dir / "execution_log.md"
    for required in (state_path, manifest_path, log_path):
        if not required.exists():
            issues.append(Issue("ERROR", scope, f"missing {required.name}"))
    if any(not path.exists() for path in (state_path, manifest_path, log_path)):
        return issues

    state_text = read_text(state_path)
    manifest_text = read_text(manifest_path)
    log_text = read_text(log_path)

    exp_id = parse_experiment_id(state_text)
    if exp_id and f"work{exp_id} code" not in code_dir.name:
        issues.append(Issue("ERROR", scope, f"experiment_id {exp_id} does not match code dir {code_dir.name}"))

    phase_statuses = parse_phase_statuses(state_text)
    experiment_status = parse_top_experiment_status(state_text)
    if experiment_status == "completed":
        for phase in ("phase1_router", "phase2_requirement", "phase3_environment", "phase4_baseline",
                      "phase5_implementation", "phase6_verification", "phase7_report", "phase8_ppt"):
            if phase_statuses.get(phase) != "completed":
                issues.append(Issue("ERROR", scope, f"experiment completed but {phase} is {phase_statuses.get(phase)!r}"))

    if re.search(r"Status:\s*running\b", log_text, flags=re.IGNORECASE):
        issues.append(Issue("ERROR", scope, "execution log contains a command still marked running"))

    for raw_path, exists in parse_manifest_paths(manifest_text):
        if exists and resolve_existing_path(root, code_dir, raw_path) is None:
            issues.append(Issue("ERROR", scope, f"manifest path marked exists but missing: {raw_path}"))

    for field, raw_path in parse_output_paths(state_text):
        if raw_path and resolve_existing_path(root, code_dir, raw_path) is None:
            level = "ERROR" if phase_statuses.get("phase7_report") == "completed" or phase_statuses.get("phase8_ppt") == "completed" else "WARNING"
            issues.append(Issue(level, scope, f"{field} points to missing path: {raw_path}"))

    verification_status = phase_statuses.get("phase6_verification")
    if verification_status == "completed" and "overall_passed: true" not in state_text:
        issues.append(Issue("ERROR", scope, "phase6 completed but verification.overall_passed is not true"))

    if phase_statuses.get("phase7_report") == "completed":
        if "report_tex:" not in state_text or "report_pdf:" not in state_text:
            issues.append(Issue("ERROR", scope, "phase7 completed but report paths are missing"))

    if phase_statuses.get("phase8_ppt") == "completed":
        if "brief_path:" not in state_text or "pptx_path:" not in state_text:
            issues.append(Issue("ERROR", scope, "phase8 completed but PPT paths are missing"))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check workflow state consistency.")
    parser.add_argument("root", nargs="?", default=".", help="Project root directory.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    workflow_dirs = sorted((root / "code").glob("work* code/_workflow"))
    if not workflow_dirs:
        print("ERROR project: no code/work* code/_workflow directories found")
        return 1

    issues: list[Issue] = []
    for workflow_dir in workflow_dirs:
        issues.extend(check_workflow(root, workflow_dir))

    errors = [issue for issue in issues if issue.level == "ERROR"]
    warnings = [issue for issue in issues if issue.level == "WARNING"]

    for issue in issues:
        print(f"{issue.level} {issue.scope}: {issue.message}")

    print(f"Checked {len(workflow_dirs)} workflow(s): {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
