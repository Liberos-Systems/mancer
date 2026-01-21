"""
Unit tests for KillCommand - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.system.kill_command import KillCommand


class TestKillCommand:
    """Unit tests for KillCommand - process termination."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_kill_basic(self, mock_get_backend, context):
        """Test basic kill command."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = KillCommand().process("1234")
        result = cmd.execute(context)

        assert result.success
        assert "1234" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_kill_with_signal(self, mock_get_backend, context):
        """Test kill with specific signal."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = KillCommand().signal("9").process("1234")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-9" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_kill_multiple_processes(self, mock_get_backend, context):
        """Test kill with multiple PIDs."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = KillCommand().processes(["1234", "5678", "9012"])
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "1234" in executed_command
        assert "5678" in executed_command
        assert "9012" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_kill_failure(self, mock_get_backend, context):
        """Test kill with failure (process not found)."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=1,
            error_message="kill: (1234): No such process",
        )
        mock_get_backend.return_value = mock_backend

        cmd = KillCommand().process("1234")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "No such process" in result.error_message
