from typing import Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class PingCommand(BaseCommand):
    """Komenda ping - testowanie połączenia sieciowego"""

    def __init__(self):
        super().__init__(name="ping")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę ping"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "PingCommand":
        """Return a new instance with an added short/long option."""
        new_instance: PingCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "PingCommand":
        """Return a new instance with a named parameter."""
        new_instance: PingCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "PingCommand":
        """Return a new instance with a boolean flag."""
        new_instance: PingCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "PingCommand":
        """Return a new instance marked to require sudo."""
        new_instance: PingCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "PingCommand":
        """Return a new instance with an added positional argument."""
        new_instance: PingCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "PingCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: PingCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla ping

    def host(self, hostname: str) -> "PingCommand":
        """Ustawia hostname/IP do pingowania"""
        return self.add_arg(hostname)

    def count(self, count: int) -> "PingCommand":
        """Opcja -c - liczba pakietów do wysłania"""
        return self.with_option("-c").with_param("count", str(count))

    def interval(self, seconds: float) -> "PingCommand":
        """Opcja -i - interwał między pakietami"""
        return self.with_option("-i").with_param("interval", str(seconds))

    def timeout(self, seconds: int) -> "PingCommand":
        """Opcja -W - timeout w sekundach"""
        return self.with_option("-W").with_param("timeout", str(seconds))
