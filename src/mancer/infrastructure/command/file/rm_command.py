from typing import List, Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class RmCommand(BaseCommand):
    """Komenda rm - usuwa pliki i katalogi"""

    def __init__(self):
        super().__init__(name="rm")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę rm"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "RmCommand":
        """Return a new instance with an added short/long option."""
        new_instance: RmCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "RmCommand":
        """Return a new instance with a named parameter."""
        new_instance: RmCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "RmCommand":
        """Return a new instance with a boolean flag."""
        new_instance: RmCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "RmCommand":
        """Return a new instance marked to require sudo."""
        new_instance: RmCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "RmCommand":
        """Return a new instance with an added positional argument."""
        new_instance: RmCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "RmCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: RmCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla rm

    def file(self, path: str) -> "RmCommand":
        """Ustawia plik do usunięcia"""
        return self.add_arg(path)

    def files(self, paths: List[str]) -> "RmCommand":
        """Ustawia wiele plików do usunięcia"""
        new_instance = self.clone()
        new_instance.args.extend(paths)
        return new_instance

    def recursive(self) -> "RmCommand":
        """Opcja -r - usuwa rekurencyjnie katalogi"""
        return self.with_option("-r")

    def force(self) -> "RmCommand":
        """Opcja -f - wymusza usunięcie bez pytania"""
        return self.with_option("-f")

    def interactive(self) -> "RmCommand":
        """Opcja -i - pyta przed usunięciem plików"""
        return self.with_option("-i")

    def verbose(self) -> "RmCommand":
        """Opcja -v - wyświetla komunikaty o usuwanych plikach"""
        return self.with_option("-v")
