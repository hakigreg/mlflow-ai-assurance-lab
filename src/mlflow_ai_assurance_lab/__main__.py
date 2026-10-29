"""Command-line entry point for the offline lab workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

from mlflow_ai_assurance_lab.application import PolicyAssistant
from mlflow_ai_assurance_lab.config import load_release_policy
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
from mlflow_ai_assurance_lab.gate import decide
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


def _gate(results_path: Path, variant: str) -> int:
    try:
        results = json.loads(results_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read evaluation results: {exc}") from exc
    variant_result = cast(dict[str, Any], results["variants"][variant])
    metrics = {str(key): float(value) for key, value in variant_result["metrics"].items()}
    decision, failed = decide(metrics, load_release_policy())
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
        return _gate(args.results, args.variant)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
