"""Loading coreutils generator configuration from YAML files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tools.coreutils_generator.models import ExecutionEnvironment


@dataclass(frozen=True)
class CommandConfig:
    """Configured command profile."""

    name: str
    arguments: list[list[str]]
    error_arguments: list[list[str]]
    tiers_enabled: list[str]
    popular_options: list[list[str]]
    allowed_options: list[str]
    max_full_combination_options: int
    working_dir: str


class ConfigLoader:
    """Helper for loading YAML configuration."""

    def __init__(self, project_root: Path):
        self._project_root = project_root
        self._config_path = project_root / "tools" / "coreutils_generator" / "config"

    def _load_yaml(self, relative: str) -> Any:
        path = self._config_path / relative
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def load_environment(self) -> ExecutionEnvironment:
        data = self._load_yaml("environments.yaml")["default"]
        return ExecutionEnvironment(
            name=data["name"],
            image_tag=data["image_tag"],
            dockerfile_path=(self._project_root / data["dockerfile_path"]).resolve(),
            run_workdir=data["run_workdir"],
            locale=data.get("locale", "C.UTF-8"),
        )

    def load_commands(self) -> list[CommandConfig]:
        raw = self._load_yaml("commands.yaml")
        defaults = raw.get("defaults", {})
        results: list[CommandConfig] = []
        for entry in raw.get("commands", []):
            merged = {**defaults, **entry}
            results.append(
                CommandConfig(
                    name=merged["name"],
                    arguments=[list(args) for args in merged.get("arguments", [[]])],
                    error_arguments=[list(args) for args in merged.get("error_arguments", [])],
                    tiers_enabled=list(merged.get("tiers_enabled", [])),
                    popular_options=[list(opts) for opts in merged.get("popular_options", [])],
                    allowed_options=list(merged.get("allowed_options", [])),
                    max_full_combination_options=int(merged.get("max_full_combination_options", 6)),
                    working_dir=merged.get("working_dir", defaults.get("working_dir", "/opt/coreutils-fixtures/files")),
                )
            )
        return results

