from typing import Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class SshCommand(BaseCommand):
    """Komenda ssh - połączenie SSH"""

    def __init__(self):
        super().__init__(name="ssh")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę ssh"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "SshCommand":
        """Return a new instance with an added short/long option."""
        new_instance: SshCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "SshCommand":
        """Return a new instance with a named parameter."""
        new_instance: SshCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "SshCommand":
        """Return a new instance with a boolean flag."""
        new_instance: SshCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "SshCommand":
        """Return a new instance marked to require sudo."""
        new_instance: SshCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "SshCommand":
        """Return a new instance with an added positional argument."""
        new_instance: SshCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "SshCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: SshCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla ssh

    def host(self, hostname: str) -> "SshCommand":
        """Ustawia hostname do połączenia"""
        return self.add_arg(hostname)

    def user(self, username: str) -> "SshCommand":
        """Opcja -l - ustawia użytkownika"""
        return self.with_option("-l").with_param("user", username)

    def port(self, port: int) -> "SshCommand":
        """Opcja -p - ustawia port"""
        return self.with_option("-p").with_param("port", str(port))

    def identity_file(self, key_file: str) -> "SshCommand":
        """Opcja -i - ustawia plik klucza prywatnego"""
        return self.with_option("-i").with_param("identity", key_file)

    def command(self, cmd: str) -> "SshCommand":
        """Wykonuje komendę na zdalnym hoście"""
        return self.add_arg(cmd)
