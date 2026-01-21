"""
Unit tests for mv command - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.file.mv_command import MvCommand
from tests.fixtures.loader import load_coreutils_output


class TestMvCommand:
    """Unit tests for MvCommand - file moving/renaming."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mv_basic_move(self, mock_get_backend, context):
        """Test basic mv command."""
        fixture = load_coreutils_output("mv", "tier0_14d5b2e535")  # mv without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MvCommand().from_source("file.txt").to_destination("newfile.txt")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0
        mock_backend.execute_command.assert_called_once()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mv_force(self, mock_get_backend, context):
        """Test mv -f force option."""
        fixture = load_coreutils_output("mv", "tier0_0e62241150")  # mv -f
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MvCommand().force().from_source("file.txt").to_destination("dest.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-f" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mv_interactive(self, mock_get_backend, context):
        """Test mv -i interactive option."""
        fixture = load_coreutils_output("mv", "tier0_14d5b2e535")  # mv without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MvCommand().interactive().from_source("file.txt").to_destination("dest.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-i" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mv_verbose(self, mock_get_backend, context):
        """Test mv -v verbose option."""
        fixture = load_coreutils_output("mv", "tier0_14d5b2e535")  # mv without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MvCommand().verbose().from_source("file.txt").to_destination("dest.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-v" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mv_backup(self, mock_get_backend, context):
        """Test mv -b backup option."""
        fixture = load_coreutils_output("mv", "tier0_04b5cd8195")  # mv -b
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MvCommand().backup().from_source("file.txt").to_destination("dest.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-b" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mv_failure(self, mock_get_backend, context):
        """Test mv with failure (file not found)."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=1,
            error_message="mv: cannot stat 'nonexistent.txt': No such file or directory",
        )
        mock_get_backend.return_value = mock_backend

        cmd = MvCommand().from_source("nonexistent.txt").to_destination("dest.txt")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "No such file or directory" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_mv_combined_options(self, mock_get_backend, context):
        """Test mv with multiple options."""
        fixture = load_coreutils_output("mv", "tier0_14d5b2e535")  # mv without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = MvCommand().force().verbose().from_source("file.txt").to_destination("dest.txt")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-f" in executed_command
        assert "-v" in executed_command
