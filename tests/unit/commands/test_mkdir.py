"""
Unit tests for mkdir command - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.file.mkdir_command import MkdirCommand
from tests.fixtures.loader import load_coreutils_output


class TestMkdirCommand:
    """Unit tests for MkdirCommand - directory creation."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mkdir_basic_creation(self, mock_get_backend, context):
        """Test basic mkdir command without options."""
        fixture = load_coreutils_output("mkdir", "tier0_c3d623fc80")  # mkdir without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MkdirCommand().directory("testdir")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0
        mock_backend.execute_command.assert_called_once()
        assert "testdir" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mkdir_with_parents(self, mock_get_backend, context):
        """Test mkdir -p creating parent directories."""
        fixture = load_coreutils_output("mkdir", "tier0_8c7e38e3c8")  # mkdir -p
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MkdirCommand().parents().directory("path/to/dir")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-p" in executed_command
        assert "path/to/dir" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mkdir_verbose(self, mock_get_backend, context):
        """Test mkdir -v with verbose output."""
        fixture = load_coreutils_output("mkdir", "tier0_53a629ee1c")  # mkdir -v
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MkdirCommand().verbose().directory("testdir")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-v" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mkdir_multiple_directories(self, mock_get_backend, context):
        """Test mkdir with multiple directories."""
        fixture = load_coreutils_output("mkdir", "tier0_c3d623fc80")  # mkdir without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MkdirCommand().directories(["dir1", "dir2", "dir3"])
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "dir1" in executed_command
        assert "dir2" in executed_command
        assert "dir3" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mkdir_with_mode(self, mock_get_backend, context):
        """Test mkdir -m with specific permissions."""
        fixture = load_coreutils_output("mkdir", "tier0_6222200f6f")  # mkdir -m 755
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MkdirCommand().mode("755").directory("testdir")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-m" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mkdir_failure(self, mock_get_backend, context):
        """Test mkdir with failure (permission denied)."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=1,
            error_message="mkdir: cannot create directory 'testdir': Permission denied",
        )
        mock_get_backend.return_value = mock_backend

        cmd = MkdirCommand().directory("/root/testdir")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "Permission denied" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mkdir_with_sudo(self, mock_get_backend, context):
        """Test mkdir with sudo."""
        fixture = load_coreutils_output("mkdir", "tier0_c3d623fc80")  # mkdir without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MkdirCommand().with_sudo().directory("/root/testdir")
        result = cmd.execute(context)

        assert result.success
        assert cmd.requires_sudo is True
