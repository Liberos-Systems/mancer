"""
Unit tests for touch command - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.file.touch_command import TouchCommand
from tests.fixtures.loader import load_coreutils_output


class TestTouchCommand:
    """Unit tests for TouchCommand - file creation/update."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_touch_basic_creation(self, mock_get_backend, context):
        """Test basic touch command."""
        fixture = load_coreutils_output("touch", "tier0_26305092c6")  # touch without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = TouchCommand().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0
        mock_backend.execute_command.assert_called_once()
        assert "file.txt" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_touch_no_create(self, mock_get_backend, context):
        """Test touch -c no-create option."""
        fixture = load_coreutils_output("touch", "tier0_a077e29310")  # touch -c
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = TouchCommand().no_create().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-c" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_touch_change_access_time(self, mock_get_backend, context):
        """Test touch -a change access time option."""
        fixture = load_coreutils_output("touch", "tier0_2ada68cbf5")  # touch -a
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = TouchCommand().change_access_time().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-a" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_touch_change_modification_time(self, mock_get_backend, context):
        """Test touch -m change modification time option."""
        fixture = load_coreutils_output("touch", "tier0_3217d21884")  # touch -m
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = TouchCommand().change_modification_time().file("file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-m" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_touch_reference(self, mock_get_backend, context):
        """Test touch -r reference option."""
        fixture = load_coreutils_output("touch", "tier0_26305092c6")  # touch without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = TouchCommand().reference("ref_file.txt").file("file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-r" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_touch_multiple_files(self, mock_get_backend, context):
        """Test touch with multiple files."""
        fixture = load_coreutils_output("touch", "tier0_26305092c6")  # touch without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = TouchCommand().files(["file1.txt", "file2.txt", "file3.txt"])
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "file1.txt" in executed_command
        assert "file2.txt" in executed_command
        assert "file3.txt" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_touch_failure(self, mock_get_backend, context):
        """Test touch with failure (permission denied)."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=1,
            error_message="touch: cannot touch '/root/file.txt': Permission denied",
        )
        mock_get_backend.return_value = mock_backend

        cmd = TouchCommand().file("/root/file.txt")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "Permission denied" in result.error_message
