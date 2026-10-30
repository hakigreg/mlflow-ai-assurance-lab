"""Command-line entry point for the offline lab workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from mlflow_ai_assurance_lab.application import PolicyAssistant
from mlflow_ai_assurance_lab.config import (
    DEFAULT_POLICY_PATH,
    ConfigurationError,
    load_release_policy,
)
from mlflow_ai_assurance_lab.evaluation import (
    DEFAULT_RESULTS_PATH,
    DEFAULT_RUNTIME_DIR,
    run_comparison,
)
from mlflow_ai_assurance_lab.evidence import (
    DEFAULT_EVIDENCE_DIR,
    generate_evidence,
    validate_evidence,
)
from mlflow_ai_assurance_lab.gate import GateInputError, assess_recorded_results
from mlflow_ai_assurance_lab.tracking import configure_offline_tracking


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="run a small traced baseline/governed demo")
    demo.add_argument("--runtime-dir", type=Path, default=DEFAULT_RUNTIME_DIR)
    evaluate = subparsers.add_parser("evaluate", help="run the complete offline comparison")
    evaluate.add_argument("--runtime-dir", type=Path, default=DEFAULT_RUNTIME_DIR)
    evaluate.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    evidence = subparsers.add_parser("evidence", help="generate evidence from latest results")
    evidence.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    evidence.add_argument("--output-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    validate = subparsers.add_parser("validate-evidence", help="validate an evidence pack")
    validate.add_argument("--output-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    gate = subparsers.add_parser("gate", help="apply release policy to a variant")
    gate.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    gate.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    gate.add_argument("--variant", choices=("baseline", "governed"), default="governed")
    return parser


def _demo(runtime_dir: Path) -> int:
    configure_offline_tracking(runtime_dir)
    requests = (
        ("DEMO-POS-001", "How many remote work days are allowed with manager approval?"),
        ("DEMO-SCOPE-001", "What will the weather be tomorrow?"),
    )
    output: dict[str, list[dict[str, Any]]] = {}
    for variant in ("baseline", "governed"):
        assistant = PolicyAssistant(variant)
        output[variant] = [assistant.ask(case_id, query) for case_id, query in requests]
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def _gate(results_path: Path, policy_path: Path, variant: str) -> int:
    try:
        results = json.loads(results_path.read_text(encoding="utf-8"))
        if not isinstance(results, dict):
            raise GateInputError("evaluation results root must be an object")
        policy = load_release_policy(policy_path)
        policy_digest = hashlib.sha256(policy_path.read_bytes()).hexdigest()
        decision, failed = assess_recorded_results(results, variant, policy, policy_digest)
    except (FileNotFoundError, json.JSONDecodeError, ConfigurationError, GateInputError) as exc:
        print(f"gate input error: {exc}", file=sys.stderr)
        return 2
    print(f"{variant}: {decision}; failed_metrics={list(failed)}")
    return 0 if decision == "PASS" else 1


def main() -> int:
    args = _parser().parse_args()
    if args.command == "demo":
        return _demo(args.runtime_dir)
    if args.command == "evaluate":
        results = run_comparison(args.runtime_dir, args.results)
        variants = results["variants"]
        print(
            f"baseline={variants['baseline']['decision']} "
            f"governed={variants['governed']['decision']} results={args.results}"
        )
        return 0
    if args.command == "evidence":
        output = generate_evidence(args.results, args.output_dir)
        print(f"Evidence generated and validated: {output}")
        return 0
    if args.command == "validate-evidence":
        validate_evidence(args.output_dir)
        print(f"Evidence validation passed: {args.output_dir}")
        return 0
    if args.command == "gate":
        return _gate(args.results, args.policy, args.variant)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
