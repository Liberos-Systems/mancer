"""Test scenario factory based on configuration data."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Sequence

from tools.coreutils_generator.config.loader import CommandConfig
from tools.coreutils_generator.generator.combination_engine import (
    CombinationCase,
    CombinationEngine,
    CombinationSettings,
)
from tools.coreutils_generator.models import CommandInvocation, CommandOption


@dataclass(frozen=True)
class ScenarioConfig:
    """Data generation parameters."""

    tiers: Sequence[str]
    include_errors: bool = True
    allowlist_tier2_only: bool = False


class TestDataFactory:
    """Connects option parser, configuration and combination engine."""

    def __init__(self, combination_engine: CombinationEngine | None = None):
        self._engine = combination_engine or CombinationEngine(CombinationSettings())

    def build_invocations(
        self,
        command_config: CommandConfig,
        options: Sequence[CommandOption],
        scenario_cfg: ScenarioConfig,
    ) -> list[CommandInvocation]:
        # Fill tokens with default values when required
        # For options requiring values, we need to handle them specially in combinations
        option_tokens: list[str] = []
        tier2_tokens: list[str] = []
        allowed = set(command_config.allowed_options or [])
        for opt in options:
            if opt.requires_value:
                if not opt.default_value:
                    continue
                if opt.token.startswith("--"):
                    # Long options: "--bytes=64" as single token
                    token_str = f"{opt.token}={opt.default_value}"
                else:
                    # Short options: "-c" and "64" as separate tokens for combination engine
                    # We'll mark it with a special format that we'll split later
                    token_str = f"{opt.token}:{opt.default_value}"
            else:
                token_str = opt.token
            option_tokens.append(token_str)
            if not allowed or opt.token in allowed or token_str in allowed:
                tier2_tokens.append(token_str)

        active_tiers = list(scenario_cfg.tiers)
        if "tier2" in active_tiers and scenario_cfg.allowlist_tier2_only and not allowed:
            active_tiers = [tier for tier in active_tiers if tier != "tier2"]
        combinations = self._engine.generate(
            option_tokens,
            command_config.popular_options,
            active_tiers,
            command_config.max_full_combination_options,
            tier2_options=tier2_tokens,
        )

        # Map option tokens back to their values for options requiring values
        option_value_map: dict[str, str] = {}
        for opt in options:
            if opt.requires_value and opt.default_value:
                if opt.token.startswith("--"):
                    option_value_map[opt.token] = opt.default_value
                else:
                    option_value_map[opt.token] = opt.default_value

        invocations: list[CommandInvocation] = []
        for case in combinations:
            # Expand options that require values
            expanded_case_options: list[str] = []
            for opt_token in case.options:
                if ":" in opt_token and not opt_token.startswith("--"):
                    # Short option with value: "-c:64" -> ["-c", "64"]
                    parts = opt_token.split(":", 1)
                    expanded_case_options.extend(parts)
                elif opt_token in option_value_map:
                    # Option token found in map, add value
                    expanded_case_options.append(opt_token)
                    expanded_case_options.append(option_value_map[opt_token])
                else:
                    expanded_case_options.append(opt_token)
            
            for args in command_config.arguments:
                invocations.append(
                    self._build_invocation(
                        command=command_config.name,
                        tier=case.tier,
                        options=expanded_case_options,
                        args=tuple(args),
                    )
                )

        if scenario_cfg.include_errors and command_config.error_arguments:
            invocations.extend(
                self._build_error_invocations(command_config, option_tokens[:1])
            )

        return invocations

    def _build_invocation(
        self,
        command: str,
        tier: str,
        options: Sequence[str],
        args: Sequence[str],
        metadata: dict | None = None,
    ) -> CommandInvocation:
        # Options are already expanded at this point (from build_invocations)
        scenario_hash = hashlib.sha1()
        scenario_hash.update(command.encode("utf-8"))
        scenario_hash.update("_".join(options).encode("utf-8"))
        scenario_hash.update("_".join(args).encode("utf-8"))
        slug = scenario_hash.hexdigest()[:10]
        scenario_id = f"{tier}_{slug}"
        return CommandInvocation(
            command=command,
            options=tuple(options),
            args=tuple(args),
            tier=tier,
            scenario_id=scenario_id,
            metadata=metadata or {},
        )

    def _build_error_invocations(
        self,
        command_config: CommandConfig,
        representative_options: Sequence[str],
    ) -> list[CommandInvocation]:
        invocations: list[CommandInvocation] = []
        for args in command_config.error_arguments:
            # Ensure at least one invocation with representative option
            option_choice = representative_options[0] if representative_options else ""
            options = tuple(filter(None, (option_choice,)))
            invocations.append(
                self._build_invocation(
                    command_config.name,
                    tier="tier3",
                    options=options,
                    args=tuple(args),
                    metadata={"error": True},
                )
            )
        return invocations

