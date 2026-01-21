from typing import Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class MvCommand(BaseCommand):
    """Komenda mv - przenosi/zmienia nazwę plików i katalogów"""

    def __init__(self):
        super().__init__(name="mv")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę mv"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "MvCommand":
        """Return a new instance with an added short/long option."""
        new_instance: MvCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "MvCommand":
        """Return a new instance with a named parameter."""
        new_instance: MvCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "MvCommand":
        """Return a new instance with a boolean flag."""
        new_instance: MvCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "MvCommand":
        """Return a new instance marked to require sudo."""
        new_instance: MvCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "MvCommand":
        """Return a new instance with an added positional argument."""
        new_instance: MvCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "MvCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: MvCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla mv

    def from_source(self, source: str) -> "MvCommand":
        """Ustawia źródło przenoszenia"""
        return self.with_param("source", source)

    def to_destination(self, destination: str) -> "MvCommand":
        """Ustawia cel przenoszenia"""
        return self.with_param("destination", destination)

    def force(self) -> "MvCommand":
        """Opcja -f - wymusza przeniesienie bez pytania"""
        return self.with_option("-f")

    def interactive(self) -> "MvCommand":
        """Opcja -i - pyta przed nadpisaniem plików"""
        return self.with_option("-i")

    def verbose(self) -> "MvCommand":
        """Opcja -v - wyświetla komunikaty o przenoszonych plikach"""
        return self.with_option("-v")

    def backup(self) -> "MvCommand":
        """Opcja -b - tworzy kopię zapasową przed nadpisaniem"""
        return self.with_option("-b")
