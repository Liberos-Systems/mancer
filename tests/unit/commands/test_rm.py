"""
Unit tests for rm command - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.file.rm_command import RmCommand
from tests.fixtures.loader import load_coreutils_output


class TestRmCommand:
    """Unit tests for RmCommand - file removal."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_basic_removal(self, mock_get_backend, context):
        """Test basic rm command."""
        fixture = load_coreutils_output("rm", "tier0_6994359b10")  # rm -f (basic success)
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0
        mock_backend.execute_command.assert_called_once()
        assert "file.txt" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_recursive(self, mock_get_backend, context):
        """Test rm -r recursive option."""
        fixture = load_coreutils_output("rm", "tier0_6994359b10")  # rm -f
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().recursive().file("directory")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-r" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_force(self, mock_get_backend, context):
        """Test rm -f force option."""
        fixture = load_coreutils_output("rm", "tier0_6994359b10")  # rm -f
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().force().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-f" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_interactive(self, mock_get_backend, context):
        """Test rm -i interactive option."""
        fixture = load_coreutils_output("rm", "tier0_6994359b10")  # rm -f
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().interactive().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-i" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_verbose(self, mock_get_backend, context):
        """Test rm -v verbose option."""
        fixture = load_coreutils_output("rm", "tier0_6994359b10")  # rm -f
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().verbose().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-v" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_multiple_files(self, mock_get_backend, context):
        """Test rm with multiple files."""
        fixture = load_coreutils_output("rm", "tier0_6994359b10")  # rm -f
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().files(["file1.txt", "file2.txt", "file3.txt"])
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "file1.txt" in executed_command
        assert "file2.txt" in executed_command
        assert "file3.txt" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_failure(self, mock_get_backend, context):
        """Test rm with failure (file not found)."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=1,
            error_message="rm: cannot remove 'nonexistent.txt': No such file or directory",
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().file("nonexistent.txt")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "No such file or directory" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_rm_combined_options(self, mock_get_backend, context):
        """Test rm with combined options."""
        fixture = load_coreutils_output("rm", "tier0_6994359b10")  # rm -f
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = RmCommand().recursive().force().verbose().file("directory")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-r" in executed_command
        assert "-f" in executed_command
        assert "-v" in executed_command
