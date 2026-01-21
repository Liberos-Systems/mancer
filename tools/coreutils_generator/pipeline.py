"""Pipeline to parse options from man, enrich defaults, plan scenarios, and run."""

from __future__ import annotations

import collections
import hashlib
import json
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

import yaml

from tools.coreutils_generator.config.loader import CommandConfig, ConfigLoader
from tools.coreutils_generator.generator.test_data_factory import ScenarioConfig, TestDataFactory
from tools.coreutils_generator.models import CommandInvocation, CommandOption
from tools.coreutils_generator.parser.help_parser import HelpParser
from tools.coreutils_generator.parser.man_parser import ManParser, ManParserError
from tools.coreutils_generator.runner.docker_runner import DockerCommandRunner
from tools.coreutils_generator.storage.output_repository import OutputRepository


class OptionEnricher:
    """Enrich options with default values using option_defaults.yaml."""

    def __init__(self, defaults_path: Path):
        raw = yaml.safe_load(defaults_path.read_text(encoding="utf-8"))
        self._global_defaults = raw.get("defaults", {})
        self._command_defaults = raw.get("commands", {})

    def enrich(self, command: str, options: Sequence[CommandOption]) -> list[CommandOption]:
        cmd_defaults = self._command_defaults.get(command, {})
        enriched: list[CommandOption] = []
        for opt in options:
            default_value = None
            if opt.requires_value:
                default_value = cmd_defaults.get(opt.token, self._global_defaults.get(opt.token))
                if default_value is None:
                    # Skip options that require value but we don't have a default
                    continue
            enriched.append(
                CommandOption(
                    token=opt.token,
                    description=opt.description,
                    requires_value=opt.requires_value,
                    default_value=default_value,
                    source=opt.source,
                )
            )
        return enriched


class ArtifactWriter:
    """Persists intermediate artifacts for observability."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.options_dir = base_dir / "_artifacts" / "options"
        self.enriched_dir = base_dir / "_artifacts" / "enriched_options"
        self.plan_dir = base_dir / "_artifacts" / "scenario_plan"
        self.report_path = base_dir / "_artifacts" / "report.json"
        self.log_dir = base_dir / "_logs"
        for d in (self.options_dir, self.enriched_dir, self.plan_dir, self.log_dir):
            d.mkdir(parents=True, exist_ok=True)

    def write_options(self, command: str, options: Sequence[CommandOption]) -> Path:
        self.options_dir.mkdir(parents=True, exist_ok=True)
        path = self.options_dir / f"{command}.json"
        payload = [asdict(opt) for opt in options]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def write_enriched_options(self, command: str, options: Sequence[CommandOption]) -> Path:
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        path = self.enriched_dir / f"{command}.json"
        payload = [asdict(opt) for opt in options]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def write_plan(self, command: str, invocations: Sequence[CommandInvocation]) -> Path:
        self.plan_dir.mkdir(parents=True, exist_ok=True)
        path = self.plan_dir / f"{command}.json"
        payload = [asdict(inv) for inv in invocations]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def write_report(self, payload: dict) -> Path:
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return self.report_path

    def log(self, command: str, message: str) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.log_dir / f"{command}.log"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(message + "\n")


class Pipeline:
    """Coordinates parse -> enrich -> plan -> run with artifacts."""

    def __init__(self, project_root: Path, artifact_dir: Path | None = None):
        self.project_root = project_root
        self.config_loader = ConfigLoader(project_root)
        self.env = self.config_loader.load_environment()
        self.repository = OutputRepository(project_root / "tests" / "fixtures" / "coreutils_outputs")
        self.artifacts = ArtifactWriter(
            artifact_dir or self.repository.base_path  # type: ignore[attr-defined]
        )
        self.man_parser = ManParser(image=self.env.image_tag)
        self.help_parser = HelpParser()
        self.enricher = OptionEnricher(project_root / "tools" / "coreutils_generator" / "config" / "option_defaults.yaml")
        self.factory = TestDataFactory()
        self.runner = DockerCommandRunner(self.env, self.project_root)

    def _is_under_project(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.project_root.resolve())
            return True
        except ValueError:
            return False

    def _clean_outputs(self, commands: Iterable[str]) -> None:
        base = self.repository.base_path
        if not self._is_under_project(base):
            raise ValueError("Cleanup path must be inside project")

        removed: list[Path] = []
        for cmd in commands:
            target = base / cmd
            if target.exists():
                shutil.rmtree(target)
                removed.append(target)

        for name in ("_artifacts", "_logs"):
            target = base / name
            if target.exists():
                shutil.rmtree(target)
                removed.append(target)

        manifest = base / "manifest.json"
        if manifest.exists():
            manifest.unlink()
            removed.append(manifest)

        self.artifacts.log_dir.mkdir(parents=True, exist_ok=True)
        cleanup_log = self.artifacts.log_dir / "cleanup.log"
        timestamp = datetime.utcnow().isoformat() + "Z"
        with cleanup_log.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] cleanup start\n")
            for path in removed:
                handle.write(f"[CLEAN] {path.relative_to(base)}\n")
            handle.write(f"[{timestamp}] cleanup end\n")

    def run(
        self,
        commands: Iterable[str],
        tiers: Sequence[str],
        limit: int | None = None,
        stage_only: str | None = None,
        dry_run: bool = False,
        clean: bool = False,
        allowlist_tier2_only: bool = False,
    ) -> None:
        command_configs = [c for c in self.config_loader.load_commands() if c.name in commands]
        if clean:
            self._clean_outputs([cfg.name for cfg in command_configs])
        self.runner.ensure_image(rebuild=False)

        report_commands: list[dict] = []

        for cfg in command_configs:
            self.artifacts.log(cfg.name, f"== {cfg.name} ==")
            option_source = "man"
            try:
                options = self.man_parser.parse(cfg.name)
                if not options:
                    raise ManParserError("No options parsed")
                self.artifacts.log(cfg.name, f"[parse] man options={len(options)}")
            except ManParserError as exc:
                self.artifacts.log(cfg.name, f"[WARN] man parse failed: {exc}; falling back to --help")
                options = self.help_parser.parse(cfg.name)
                option_source = "help"
                self.artifacts.log(cfg.name, f"[parse] help options={len(options)}")

            if not options:
                self.artifacts.log(cfg.name, "[WARN] No options parsed; skipping command")
                continue

            self.artifacts.write_options(cfg.name, options)

            enriched = self.enricher.enrich(cfg.name, options)
            self.artifacts.write_enriched_options(cfg.name, enriched)
            self.artifacts.log(cfg.name, f"[enrich] options={len(enriched)} (input={len(options)})")
            if not enriched:
                self.artifacts.log(cfg.name, "[WARN] No enriched options after defaults; skipping")
                continue

            if allowlist_tier2_only and "tier2" in tiers and not cfg.allowed_options:
                self.artifacts.log(
                    cfg.name,
                    "[INFO] Skipping tier2 (no allowed_options and --allowlist-tier2 enabled)",
                )
            active_tiers = [tier for tier in tiers if tier in cfg.tiers_enabled]

            scenario_cfg = ScenarioConfig(
                tiers=active_tiers,
                include_errors="tier3" in active_tiers,
                allowlist_tier2_only=allowlist_tier2_only,
            )
            invocations = self.factory.build_invocations(cfg, enriched, scenario_cfg)
            if limit:
                invocations = invocations[:limit]
            if not invocations:
                self.artifacts.log(cfg.name, "[WARN] No scenarios after planning; skipping command")
                continue

            self.artifacts.write_plan(cfg.name, invocations)
            tier_counts = collections.Counter(inv.tier for inv in invocations)
            self.artifacts.log(
                cfg.name,
                f"[plan] scenarios={len(invocations)} tiers={dict(tier_counts)}",
            )

            planned_by_tier = dict(tier_counts)
            cmd_report = {
                "command": cfg.name,
                "option_source": option_source,
                "image_tag": self.env.image_tag,
                "planned": {"total": len(invocations), "by_tier": planned_by_tier},
                "executed": {"total": 0, "by_tier": {}},
                "exit_codes": {},
                "success_rate": 0.0,
                "unique_stdout": 0,
                "stdout_top": [],
            }

            if stage_only in {"parse", "enrich", "plan"} or dry_run:
                report_commands.append(cmd_report)
                continue

            exit_codes = collections.Counter()
            executed_by_tier = collections.Counter()
            stdout_hashes = collections.Counter()
            stdout_lengths: dict[str, int] = {}
            success_count = 0

            for idx, invocation in enumerate(invocations, start=1):
                result = self.runner.run(invocation, cfg.working_dir)
                meta = {**invocation.metadata, "option_source": option_source}
                patched_invocation = CommandInvocation(
                    command=invocation.command,
                    options=invocation.options,
                    args=invocation.args,
                    tier=invocation.tier,
                    scenario_id=invocation.scenario_id,
                    metadata=meta,
                )
                self.repository.save(patched_invocation, result)

                exit_codes[result.exit_code] += 1
                executed_by_tier[invocation.tier] += 1
                if result.exit_code == 0:
                    success_count += 1
                stdout_hash = hashlib.sha1(result.stdout.encode("utf-8")).hexdigest()
                stdout_hashes[stdout_hash] += 1
                stdout_lengths.setdefault(stdout_hash, len(result.stdout))

                if idx % 20 == 0 or idx == len(invocations):
                    self.artifacts.log(
                        cfg.name,
                        f"[run] executed {idx}/{len(invocations)} scenarios",
                    )

            executed_total = sum(executed_by_tier.values())
            cmd_report["executed"] = {
                "total": executed_total,
                "by_tier": dict(executed_by_tier),
            }
            cmd_report["exit_codes"] = dict(exit_codes)
            cmd_report["success_rate"] = success_count / executed_total if executed_total else 0.0
            cmd_report["unique_stdout"] = len(stdout_hashes)
            cmd_report["stdout_top"] = [
                {"hash": hash_, "count": count, "length": stdout_lengths.get(hash_, 0)}
                for hash_, count in stdout_hashes.most_common(5)
            ]

            report_commands.append(cmd_report)

        if report_commands:
            report_payload = {
                "image_tag": self.env.image_tag,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "commands": report_commands,
            }
            self.artifacts.write_report(report_payload)
            summary_lines = []
            for cmd_report in report_commands:
                summary_lines.append(
                    f"{cmd_report['command']}: planned={cmd_report['planned']['total']} "
                    f"executed={cmd_report['executed']['total']} "
                    f"success={cmd_report['success_rate']:.1%} "
                    f"exit_codes={cmd_report['exit_codes']}"
                )
            print("== Pipeline summary ==")
            for line in summary_lines:
                print(" - " + line)
            print(f"Raport zapisany w {self.artifacts.report_path}")

