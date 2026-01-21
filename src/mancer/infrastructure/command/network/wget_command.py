from typing import Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class WgetCommand(BaseCommand):
    """Komenda wget - pobieranie plików przez HTTP/HTTPS/FTP"""

    def __init__(self):
        super().__init__(name="wget")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę wget"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "WgetCommand":
        """Return a new instance with an added short/long option."""
        new_instance: WgetCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "WgetCommand":
        """Return a new instance with a named parameter."""
        new_instance: WgetCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "WgetCommand":
        """Return a new instance with a boolean flag."""
        new_instance: WgetCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "WgetCommand":
        """Return a new instance marked to require sudo."""
        new_instance: WgetCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "WgetCommand":
        """Return a new instance with an added positional argument."""
        new_instance: WgetCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "WgetCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: WgetCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla wget

    def url(self, url: str) -> "WgetCommand":
        """Ustawia URL do pobrania"""
        return self.add_arg(url)

    def output_document(self, file: str) -> "WgetCommand":
        """Opcja -O - zapisuje do pliku"""
        return self.with_option("-O").with_param("output", file)

    def quiet(self) -> "WgetCommand":
        """Opcja -q - tryb cichy"""
        return self.with_option("-q")

    def verbose(self) -> "WgetCommand":
        """Opcja -v - tryb verbose"""
        return self.with_option("-v")

    def recursive(self) -> "WgetCommand":
        """Opcja -r - pobiera rekurencyjnie"""
        return self.with_option("-r")

    def continue_download(self) -> "WgetCommand":
        """Opcja -c - kontynuuje przerwane pobieranie"""
        return self.with_option("-c")
