"""Parser extracting options from `man` pages (OPTIONS section)."""

from __future__ import annotations

import re
import subprocess
from typing import Iterable, List

from tools.coreutils_generator.models import CommandOption

# Heuristics:
# - detect OPTIONS section
# - stop on next all-caps heading or end of file
# - parse lines containing short/long forms
OPTION_LINE = re.compile(
    r"^\s{0,10}(-{1,2}[A-Za-z0-9][\w-]*"
    r"(?:[ =]\w+|=\w+)?)(?:,\s*(-{1,2}[A-Za-z0-9][\w-]*(?:[ =]\w+|=\w+)?))?"
)

SECTION_HEADER = re.compile(r"^[A-Z][A-Z0-9 _-]{3,}$")


class ManParserError(RuntimeError):
    """Error parsing `man` output."""


class ManParser:
    """Extracts command options by parsing `man <command>` output."""

    def __init__(self, timeout: float = 5.0, image: str | None = None):
        self._timeout = timeout
        self._image = image

    def parse(self, command: str) -> list[CommandOption]:
        lines = self._read_man(command)
        option_lines = self._extract_options_section(lines)
        return list(self._parse_option_lines(option_lines))

    def _read_man(self, command: str) -> list[str]:
        try:
            if self._image:
                proc = subprocess.run(
                    [
                        "docker",
                        "run",
                        "--rm",
                        "--entrypoint=man",
                        self._image,
                        "-P",
                        "cat",
                        command,
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                )
            else:
                proc = subprocess.run(
                    ["man", command],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ManParserError(f"Failed to run `man {command}`: {exc}") from exc

        text = proc.stdout or proc.stderr
        if not text:
            raise ManParserError(f"`man {command}` returned no output.")

        # Use col -b to strip formatting if available
        try:
            col = subprocess.run(
                ["col", "-b"],
                input=text,
                capture_output=True,
                text=True,
                check=False,
            )
            if col.stdout:
                text = col.stdout
        except Exception:
            # Fallback to raw text
            pass

        return text.splitlines()

    def _extract_options_section(self, lines: list[str]) -> list[str]:
        in_options = False
        collected: List[str] = []
        for line in lines:
            stripped = line.strip()
            if not in_options and stripped.upper() == "OPTIONS":
                in_options = True
                continue
            if in_options:
                # Stop at next section header
                if SECTION_HEADER.match(stripped) and stripped.upper() != "OPTIONS":
                    break
                collected.append(line)
        if not collected:
            # Fallback: parse whole document if OPTIONS section not found
            return lines
        return collected

    def _parse_option_lines(self, lines: Iterable[str]) -> Iterable[CommandOption]:
        seen = set()
        for line in lines:
            match = OPTION_LINE.match(line)
            if not match:
                continue
            short, long = match.groups()
            raw_tokens = [tok for tok in (short, long) if tok]
            # Check if line indicates value requirement (e.g., "=[-]NUM", "NUM", etc.)
            line_lower = line.lower()
            has_value_indicator = any(
                pattern in line_lower
                for pattern in ["=num", "=when", "=size", "=format", "=style", "=file", "=dir", "=path"]
            ) or re.search(r'=\[[^\]]*\]\w+', line_lower) is not None
            
            normalized = [self._normalize_token(tok) for tok in raw_tokens]
            requires_any = any(req for _, req in normalized) or has_value_indicator
            for tok, req in normalized:
                token_clean = tok
                requires_value = requires_any or req
                if token_clean in seen:
                    continue
                seen.add(token_clean)
                yield CommandOption(
                    token=token_clean,
                    description="",
                    requires_value=requires_value,
                    source="man",
                )

    def _normalize_token(self, token: str) -> tuple[str, bool]:
        """Normalize token, detect if requires value."""
        tok = token.strip()
        # Replace occurrences like '--color[=WHEN]' if any appear
        tok = tok.replace("[", "").replace("]", "")
        requires = False
        if "=" in tok or " " in tok:
            requires = True
            # Normalize to equals for single token
            tok = tok.replace(" ", "=")
        return tok, requires


def parse_man_options(command: str) -> list[CommandOption]:
    """Convenience function."""
    return ManParser().parse(command)

