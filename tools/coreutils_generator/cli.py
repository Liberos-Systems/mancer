"""CLI for generating reference coreutils command outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.coreutils_generator.config.loader import ConfigLoader
from tools.coreutils_generator.generator.test_data_factory import ScenarioConfig, TestDataFactory
from tools.coreutils_generator.parser.help_parser import HelpParser, HelpParserError
from tools.coreutils_generator.pipeline import Pipeline
from tools.coreutils_generator.runner.docker_runner import DockerCommandRunner
from tools.coreutils_generator.storage.output_repository import OutputRepository


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generator of coreutils command outputs (Docker).")
    parser.add_argument(
        "--commands",
        nargs="*",
        help="List of commands to generate (default: all from commands.yaml).",
    )
    parser.add_argument(
        "--tiers",
        nargs="*",
        default=["tier0", "tier1"],
        help="List of active tiers (default: tier0 tier1).",
    )
    parser.add_argument(
        "--rebuild-image",
        action="store_true",
        help="Force Docker image rebuild.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't execute commands – print planned scenarios.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Global limit of scenarios per command (0 = no limit).",
    )
    # Pipeline-specific
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Use man-based pipeline with artifacts/logs.",
    )
    parser.add_argument(
        "--pipeline-stage",
        choices=["all", "parse", "enrich", "plan", "run"],
        default="all",
        help="Run only selected stage (pipeline mode).",
    )
    parser.add_argument(
        "--artifact-dir",
        type=str,
        help="Custom artifact directory for pipeline (defaults to fixtures dir).",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Safely clean fixtures (_artifacts/_logs/manifest/command dirs) before run.",
    )
    parser.add_argument(
        "--allowlist-tier2",
        action="store_true",
        help="Generate tier2 only when allowed_options are defined for the command.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    project_root = Path(__file__).resolve().parents[2]
    # Pipeline mode (man-based, artifacts)
    if args.pipeline:
        pipeline = Pipeline(project_root, Path(args.artifact_dir) if args.artifact_dir else None)
        command_configs = ConfigLoader(project_root).load_commands()
        selected_names = set(args.commands or [cfg.name for cfg in command_configs])
        tiers = args.tiers
        stage_only = None if args.pipeline_stage == "all" else args.pipeline_stage
        limit = args.limit if args.limit > 0 else None
        pipeline.run(
            selected_names,
            tiers,
            limit=limit,
            stage_only=stage_only,
            dry_run=args.dry_run,
            clean=args.clean,
            allowlist_tier2_only=args.allowlist_tier2,
        )
        return 0

    # Legacy/help-based flow
    config_loader = ConfigLoader(project_root)
    env = config_loader.load_environment()
    command_configs = config_loader.load_commands()
    selected_names = set(args.commands or [cfg.name for cfg in command_configs])

    parser = HelpParser()
    factory = TestDataFactory()
    runner = DockerCommandRunner(env, project_root)
    repository = OutputRepository(project_root / "tests" / "fixtures" / "coreutils_outputs")

    runner.ensure_image(rebuild=args.rebuild_image)

    for config in command_configs:
        if config.name not in selected_names:
            continue
        try:
            options = parser.parse(config.name)
        except HelpParserError as exc:
            print(f"[WARN] Skipped {config.name}: {exc}", file=sys.stderr)
            continue

        scenario_cfg = ScenarioConfig(
            tiers=args.tiers,
            include_errors="tier3" in args.tiers,
            allowlist_tier2_only=args.allowlist_tier2,
        )
        invocations = factory.build_invocations(config, options, scenario_cfg)
        if args.limit:
            invocations = invocations[: args.limit]

        print(f"[INFO] {config.name}: {len(invocations)} scenariuszy")
        if args.dry_run:
            for invocation in invocations:
                print(" ", invocation.tier, invocation.options, invocation.args)
            continue

        for invocation in invocations:
            result = runner.run(invocation, config.working_dir)
            repository.save(invocation, result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

