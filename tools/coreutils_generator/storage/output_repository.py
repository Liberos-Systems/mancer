"""Persistence of command outputs in JSON structure."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.coreutils_generator.models import CommandInvocation, ExecutionResult


class OutputRepository:
    """Saves individual results and maintains manifest."""

    def __init__(self, base_path: Path):
        self._base_path = base_path
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._base_path / "manifest.json"

    @property
    def base_path(self) -> Path:
        return self._base_path

    def save(self, invocation: CommandInvocation, result: ExecutionResult) -> Path:
        command_dir = self._base_path / invocation.command
        command_dir.mkdir(parents=True, exist_ok=True)
        file_path = command_dir / f"{invocation.scenario_id}.json"
        payload = self._build_payload(invocation, result)
        file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self._update_manifest(invocation, file_path)
        return file_path

    def _build_payload(self, invocation: CommandInvocation, result: ExecutionResult) -> dict[str, Any]:
        return {
            "command": invocation.command,
            "tier": invocation.tier,
            "scenario_id": invocation.scenario_id,
            "options": list(invocation.options),
            "args": list(invocation.args),
            "metadata": invocation.metadata,
            "environment": result.environment,
            "full_command": result.full_command,
            "result": {
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_ms": result.duration_ms,
            },
            "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }

    def _update_manifest(self, invocation: CommandInvocation, file_path: Path) -> None:
        manifest = []
        if self._manifest_path.exists():
            manifest = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        entry = {
            "command": invocation.command,
            "scenario_id": invocation.scenario_id,
            "tier": invocation.tier,
            "file": str(file_path.relative_to(self._base_path)),
            "option_source": invocation.metadata.get("option_source") if isinstance(invocation.metadata, dict) else None,
        }
        manifest = [item for item in manifest if item["scenario_id"] != invocation.scenario_id]
        manifest.append(entry)
        self._manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

