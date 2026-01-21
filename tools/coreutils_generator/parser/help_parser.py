"""Parser extracting options from `--help` outputs."""

from __future__ import annotations

import re
import shlex
import subprocess
from typing import Iterable

from tools.coreutils_generator.models import CommandOption

OPTION_PATTERN = re.compile(
    r"^\s{0,6}(-\S+)(?:,\s*(--[a-zA-Z0-9][\w-]*)(?:[= ]\S+)?)?\s+(.*)$"
)


class HelpParserError(RuntimeError):
    """Error parsing data from `--help`."""


class HelpParser:
    """Extracts command options by running `command --help`."""

    def __init__(self, timeout: float = 5.0):
        self._timeout = timeout

    def parse(self, command: str) -> list[CommandOption]:
        try:
            result = subprocess.run(
                [command, "--help"],
                check=False,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise HelpParserError(f"Failed to run `{command} --help`: {exc}") from exc

        help_text = result.stdout or result.stderr
        if not help_text:
            raise HelpParserError(f"Command `{command} --help` returned no help text.")
        return list(self._parse_help(help_text.splitlines()))

    def _parse_help(self, lines: Iterable[str]) -> Iterable[CommandOption]:
        for line in lines:
            match = OPTION_PATTERN.match(line)
            if not match:
                continue
            short, long, description = match.groups()
            tokens = [token for token in (short, long) if token]

            # Clean up tokens - remove commas and normalize
            cleaned_tokens = []
            for token in tokens:
                # Remove trailing commas and clean up
                cleaned = token.strip().rstrip(',')
                # Remove any translated parameter values (e.g., =ROZMIAR -> =SIZE)
                if '=' in cleaned:
                    base_option = cleaned.split('=')[0]
                    # For now, just use the base option without translated values
                    cleaned_tokens.append(base_option)
                else:
                    cleaned_tokens.append(cleaned)

            # Determine if any option requires a value
            requires_value = any(
                token.endswith(("=SIZE", "=FILE", "=WHEN", "=WORD", "=STYLE", "=TIME"))
                for token in cleaned_tokens
            )

            for token in cleaned_tokens:
                yield CommandOption(
                    token=token,
                    description=description.strip(),
                    requires_value=requires_value
                )


def preview_help(command: str) -> list[str]:
    """Returns raw help lines – diagnostic helper tool."""

    parser = HelpParser()
    options = parser.parse(command)
    return [shlex.join([opt.token, "#", opt.description]) for opt in options]


