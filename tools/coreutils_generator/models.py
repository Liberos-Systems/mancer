"""Shared data models for coreutils generator."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandOption:
    """Description of single command switch."""

    token: str
    description: str
    requires_value: bool = False
    default_value: str | None = None
    source: str = "help"  # e.g. "man" or "help"


@dataclass(frozen=True)
class CommandInvocation:
    """Normalized command invocation."""

    command: str
    options: tuple[str, ...]
    args: tuple[str, ...]
    tier: str
    scenario_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionEnvironment:
    """Description of execution environment."""

    name: str
    image_tag: str
    dockerfile_path: Path
    run_workdir: str
    locale: str = "C.UTF-8"


@dataclass(frozen=True)
class ExecutionResult:
    """Result of command execution in container."""

    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    full_command: str
    environment: str


