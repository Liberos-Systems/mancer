"""Alternative runner using LXC container."""

from __future__ import annotations

import shlex
import subprocess
import time
from typing import Sequence

from tools.coreutils_generator.models import CommandInvocation, ExecutionResult


class LxcCommandRunner:
    """Executes commands inside existing LXC container."""

    def __init__(self, container_name: str, workdir: str = "/"):
        self._container = container_name
        self._workdir = workdir

    def run(self, invocation: CommandInvocation) -> ExecutionResult:
        command_parts = [invocation.command, *invocation.options, *invocation.args]
        command_str = shlex.join(command_parts)
        bash_command = f"cd {shlex.quote(self._workdir)} && {command_str}"
        lxc_cmd = [
            "lxc",
            "exec",
            self._container,
            "--",
            "/bin/bash",
            "-c",
            bash_command,
        ]

        start = time.perf_counter()
        process = subprocess.run(
            lxc_cmd,
            capture_output=True,
            text=True,
        )
        duration = (time.perf_counter() - start) * 1000

        return ExecutionResult(
            stdout=process.stdout,
            stderr=process.stderr,
            exit_code=process.returncode,
            duration_ms=duration,
            full_command=command_str,
            environment=f"lxc:{self._container}",
        )


