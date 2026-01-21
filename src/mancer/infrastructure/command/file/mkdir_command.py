from typing import List, Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class MkdirCommand(BaseCommand):
    """Komenda mkdir - tworzy katalogi"""

    def __init__(self):
        super().__init__(name="mkdir")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę mkdir"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "MkdirCommand":
        """Return a new instance with an added short/long option (e.g., -p)."""
        new_instance: MkdirCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "MkdirCommand":
        """Return a new instance with a named parameter."""
        new_instance: MkdirCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "MkdirCommand":
        """Return a new instance with a boolean flag."""
        new_instance: MkdirCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "MkdirCommand":
        """Return a new instance marked to require sudo."""
        new_instance: MkdirCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "MkdirCommand":
        """Return a new instance with an added positional argument."""
        new_instance: MkdirCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "MkdirCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: MkdirCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla mkdir

    def directory(self, path: str) -> "MkdirCommand":
        """Ustawia ścieżkę katalogu do utworzenia"""
        return self.add_arg(path)

    def directories(self, paths: List[str]) -> "MkdirCommand":
        """Ustawia wiele ścieżek katalogów do utworzenia"""
        new_instance = self.clone()
        new_instance.args.extend(paths)
        return new_instance

    def parents(self) -> "MkdirCommand":
        """Opcja -p - tworzy katalogi nadrzędne jeśli nie istnieją"""
        return self.with_option("-p")

    def verbose(self) -> "MkdirCommand":
        """Opcja -v - wyświetla komunikaty o utworzonych katalogach"""
        return self.with_option("-v")

    def mode(self, mode: str) -> "MkdirCommand":
        """Opcja -m - ustawia uprawnienia dla katalogów"""
        return self.with_option("-m").with_param("mode", mode)
