from typing import Any, List, Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class KillCommand(BaseCommand):
    """Komenda kill - wysyła sygnały do procesów"""

    def __init__(self):
        super().__init__(name="kill")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę kill"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "KillCommand":
        """Return a new instance with an added short/long option."""
        new_instance: KillCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "KillCommand":
        """Return a new instance with a named parameter."""
        new_instance: KillCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "KillCommand":
        """Return a new instance with a boolean flag."""
        new_instance: KillCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "KillCommand":
        """Return a new instance marked to require sudo."""
        new_instance: KillCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "KillCommand":
        """Return a new instance with an added positional argument."""
        new_instance: KillCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "KillCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: KillCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla kill

    def signal(self, sig: str) -> "KillCommand":
        """Ustawia sygnał do wysłania (np. -9, -15, -TERM)"""
        return self.with_option(f"-{sig}")

    def process(self, pid: str) -> "KillCommand":
        """Ustawia PID procesu do zabicia"""
        return self.add_arg(pid)

    def processes(self, pids: List[str]) -> "KillCommand":
        """Ustawia wiele PID procesów"""
        new_instance = self.clone()
        new_instance.args.extend(pids)
        return new_instance
