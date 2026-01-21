from typing import List, Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class TouchCommand(BaseCommand):
    """Komenda touch - tworzy/aktualizuje pliki"""

    def __init__(self):
        super().__init__(name="touch")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę touch"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "TouchCommand":
        """Return a new instance with an added short/long option."""
        new_instance: TouchCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "TouchCommand":
        """Return a new instance with a named parameter."""
        new_instance: TouchCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "TouchCommand":
        """Return a new instance with a boolean flag."""
        new_instance: TouchCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "TouchCommand":
        """Return a new instance marked to require sudo."""
        new_instance: TouchCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "TouchCommand":
        """Return a new instance with an added positional argument."""
        new_instance: TouchCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "TouchCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: TouchCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla touch

    def file(self, path: str) -> "TouchCommand":
        """Ustawia plik do utworzenia/aktualizacji"""
        return self.add_arg(path)

    def files(self, paths: List[str]) -> "TouchCommand":
        """Ustawia wiele plików do utworzenia/aktualizacji"""
        new_instance = self.clone()
        new_instance.args.extend(paths)
        return new_instance

    def change_access_time(self) -> "TouchCommand":
        """Opcja -a - zmienia tylko czas dostępu"""
        return self.with_option("-a")

    def change_modification_time(self) -> "TouchCommand":
        """Opcja -m - zmienia tylko czas modyfikacji"""
        return self.with_option("-m")

    def no_create(self) -> "TouchCommand":
        """Opcja -c - nie tworzy plików jeśli nie istnieją"""
        return self.with_option("-c")

    def reference(self, ref_file: str) -> "TouchCommand":
        """Opcja -r - używa czasu z pliku referencyjnego"""
        return self.with_option("-r").with_param("reference", ref_file)
