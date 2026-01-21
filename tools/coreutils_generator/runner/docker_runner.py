"""Runner executing coreutils commands in Docker containers."""

from __future__ import annotations

import shlex
import subprocess
import time
from pathlib import Path
from typing import Sequence

from tools.coreutils_generator.models import CommandInvocation, ExecutionEnvironment, ExecutionResult


class DockerBuildError(RuntimeError):
    """Docker image build error."""


class DockerExecutionError(RuntimeError):
    """Command execution error in container."""


class DockerCommandRunner:
    """Manages image building and container execution."""

    def __init__(self, environment: ExecutionEnvironment, project_root: Path):
        self._env = environment
        self._project_root = project_root

    def ensure_image(self, rebuild: bool = False) -> None:
        if not rebuild and self._image_exists():
            return
        self._build_image()

    def run(self, invocation: CommandInvocation, working_dir: str | None = None) -> ExecutionResult:
        working_dir = working_dir or self._env.run_workdir
        command_parts = [invocation.command, *invocation.options, *invocation.args]
        command_str = shlex.join(command_parts)
        bash_command = f"cd {shlex.quote(working_dir)} && {command_str}"
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--env",
            f"LC_ALL={self._env.locale}",
            self._env.image_tag,
            "/bin/bash",
            "-c",
            bash_command,
        ]

        start = time.perf_counter()
        process = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            cwd=self._project_root,
        )
        duration = (time.perf_counter() - start) * 1000

        return ExecutionResult(
            stdout=process.stdout,
            stderr=process.stderr,
            exit_code=process.returncode,
            duration_ms=duration,
            full_command=command_str,
            environment=self._env.name,
        )

    def _image_exists(self) -> bool:
        result = subprocess.run(
            ["docker", "image", "inspect", self._env.image_tag],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _build_image(self) -> None:
        dockerfile = self._env.dockerfile_path
        context = dockerfile.parent
        result = subprocess.run(
            [
                "docker",
                "build",
                "-t",
                self._env.image_tag,
                "-f",
                str(dockerfile),
                str(context),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise DockerBuildError(
                f"Failed to build image {self._env.image_tag}:\n{result.stderr}"
            )

