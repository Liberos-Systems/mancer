from typing import Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class ServiceCommand(BaseCommand):
    """Komenda service - zarządzanie usługami (legacy sysvinit)"""

    def __init__(self):
        super().__init__(name="service")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę service"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "ServiceCommand":
        """Return a new instance with an added short/long option."""
        new_instance: ServiceCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "ServiceCommand":
        """Return a new instance with a named parameter."""
        new_instance: ServiceCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "ServiceCommand":
        """Return a new instance with a boolean flag."""
        new_instance: ServiceCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "ServiceCommand":
        """Return a new instance marked to require sudo."""
        new_instance: ServiceCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "ServiceCommand":
        """Return a new instance with an added positional argument."""
        new_instance: ServiceCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "ServiceCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: ServiceCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla service

    def service_name(self, name: str) -> "ServiceCommand":
        """Ustawia nazwę usługi"""
        return self.add_arg(name)

    def start(self) -> "ServiceCommand":
        """Uruchamia usługę"""
        return self.add_arg("start")

    def stop(self) -> "ServiceCommand":
        """Zatrzymuje usługę"""
        return self.add_arg("stop")

    def restart(self) -> "ServiceCommand":
        """Restartuje usługę"""
        return self.add_arg("restart")

    def status(self) -> "ServiceCommand":
        """Sprawdza status usługi"""
        return self.add_arg("status")

    def reload(self) -> "ServiceCommand":
        """Przeładowuje konfigurację usługi"""
        return self.add_arg("reload")
