from typing import Optional

from ....domain.model.command_context import CommandContext
from ....domain.model.command_result import CommandResult
from ....domain.model.data_format import DataFormat
from ..base_command import BaseCommand, ParamValue


class CronCommand(BaseCommand):
    """Komenda cron - zarządzanie zadaniami cron"""

    def __init__(self):
        super().__init__(name="crontab")

    def execute(self, context: CommandContext, input_result: Optional[CommandResult] = None) -> CommandResult:
        """Wykonuje komendę crontab"""
        cmd_str = self.build_command()
        backend = self._get_backend(context)
        return backend.execute_command(cmd_str, working_dir=context.current_directory)

    def with_option(self, option: str) -> "CronCommand":
        """Return a new instance with an added short/long option."""
        new_instance: CronCommand = self.clone()
        new_instance.options.append(option)
        return new_instance

    def with_param(self, name: str, value: ParamValue) -> "CronCommand":
        """Return a new instance with a named parameter."""
        new_instance: CronCommand = self.clone()
        new_instance.parameters[name] = value
        return new_instance

    def with_flag(self, flag: str) -> "CronCommand":
        """Return a new instance with a boolean flag."""
        new_instance: CronCommand = self.clone()
        new_instance.flags.append(flag)
        return new_instance

    def with_sudo(self) -> "CronCommand":
        """Return a new instance marked to require sudo."""
        new_instance: CronCommand = self.clone()
        new_instance.requires_sudo = True
        return new_instance

    def add_arg(self, arg: str) -> "CronCommand":
        """Return a new instance with an added positional argument."""
        new_instance: CronCommand = self.clone()
        new_instance.args.append(arg)
        return new_instance

    def with_data_format(self, format_type: DataFormat) -> "CronCommand":
        """Return a new instance with a preferred output data format."""
        new_instance: CronCommand = self.clone()
        new_instance.preferred_data_format = format_type
        return new_instance

    # Metody specyficzne dla crontab

    def list(self) -> "CronCommand":
        """Opcja -l - wyświetla listę zadań cron"""
        return self.with_option("-l")

    def edit(self) -> "CronCommand":
        """Opcja -e - edytuje zadania cron"""
        return self.with_option("-e")

    def remove(self) -> "CronCommand":
        """Opcja -r - usuwa wszystkie zadania cron"""
        return self.with_option("-r")

    def user(self, username: str) -> "CronCommand":
        """Opcja -u - zarządza zadaniami dla użytkownika"""
        return self.with_option("-u").with_param("user", username)
