"""
Unit tests for SshCommand - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.network.ssh_command import SshCommand


class TestSshCommand:
    """Unit tests for SshCommand - SSH connection."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ssh_basic_connection(self, mock_get_backend, context):
        """Test basic ssh connection."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = SshCommand().host("example.com")
        result = cmd.execute(context)

        assert result.success
        assert "example.com" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ssh_with_user(self, mock_get_backend, context):
        """Test ssh -l user option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = SshCommand().user("admin").host("example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-l" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ssh_with_port(self, mock_get_backend, context):
        """Test ssh -p port option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = SshCommand().port(2222).host("example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-p" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ssh_with_identity(self, mock_get_backend, context):
        """Test ssh -i identity file option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = SshCommand().identity_file("~/.ssh/id_rsa").host("example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-i" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ssh_with_command(self, mock_get_backend, context):
        """Test ssh with remote command execution."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="file1.txt\nfile2.txt\n",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = SshCommand().host("example.com").command("ls")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "ls" in executed_command
