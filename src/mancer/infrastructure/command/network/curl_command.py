from typing import Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class CurlCommand(BaseCommand):
    """Komenda curl - pobieranie danych przez HTTP/HTTPS"""

    def __init__(self):
        super().__init__(name="curl")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę curl"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "CurlCommand":
        """Return a new instance with an added short/long option."""
        new_instance: CurlCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "CurlCommand":
        """Return a new instance with a named parameter."""
        new_instance: CurlCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "CurlCommand":
        """Return a new instance with a boolean flag."""
        new_instance: CurlCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "CurlCommand":
        """Return a new instance marked to require sudo."""
        new_instance: CurlCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "CurlCommand":
        """Return a new instance with an added positional argument."""
        new_instance: CurlCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "CurlCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: CurlCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla curl

    def url(self, url: str) -> "CurlCommand":
        """Ustawia URL do pobrania"""
        return self.add_arg(url)

    def output(self, file: str) -> "CurlCommand":
        """Opcja -o - zapisuje wyjście do pliku"""
        return self.with_option("-o").with_param("output", file)

    def silent(self) -> "CurlCommand":
        """Opcja -s - tryb cichy (bez progress bara)"""
        return self.with_option("-s")

    def verbose(self) -> "CurlCommand":
        """Opcja -v - tryb verbose"""
        return self.with_option("-v")

    def header(self, header: str) -> "CurlCommand":
        """Opcja -H - dodaje nagłówek HTTP"""
        return self.with_option("-H").with_param("header", header)

    def method(self, method: str) -> "CurlCommand":
        """Opcja -X - ustawia metodę HTTP"""
        return self.with_option("-X").with_param("method", method)

    def data(self, data: str) -> "CurlCommand":
        """Opcja -d - wysyła dane POST"""
        return self.with_option("-d").with_param("data", data)
