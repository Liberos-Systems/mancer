"""
Unit tests for WgetCommand - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.network.wget_command import WgetCommand


class TestWgetCommand:
    """Unit tests for WgetCommand - file download."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wget_basic_download(self, mock_get_backend, context):
        """Test basic wget download."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="--2024-01-01 12:00:00--  https://example.com/file.txt\nSaving to: 'file.txt'\n",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = WgetCommand().url("https://example.com/file.txt")
        result = cmd.execute(context)

        assert result.success
        assert "https://example.com/file.txt" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wget_quiet(self, mock_get_backend, context):
        """Test wget -q quiet option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = WgetCommand().quiet().url("https://example.com/file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-q" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wget_verbose(self, mock_get_backend, context):
        """Test wget -v verbose option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="--2024-01-01 12:00:00--  https://example.com/file.txt\nConnecting to example.com...\n",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = WgetCommand().verbose().url("https://example.com/file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-v" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wget_output_document(self, mock_get_backend, context):
        """Test wget -O output document option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = WgetCommand().output_document("downloaded.txt").url("https://example.com/file.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-O" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wget_recursive(self, mock_get_backend, context):
        """Test wget -r recursive option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = WgetCommand().recursive().url("https://example.com/")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-r" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wget_continue(self, mock_get_backend, context):
        """Test wget -c continue download option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = WgetCommand().continue_download().url("https://example.com/largefile.zip")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-c" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wget_failure(self, mock_get_backend, context):
        """Test wget with failure (404 Not Found)."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=8,
            error_message="404 Not Found",
        )
        mock_get_backend.return_value = mock_backend

        cmd = WgetCommand().url("https://example.com/nonexistent.txt")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 8
