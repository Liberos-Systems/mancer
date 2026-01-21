"""
Unit tests for echo command - all scenarios in one focused file
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.system.echo_command import EchoCommand
from tests.fixtures.loader import load_coreutils_output


class TestEchoCommand:
    """Unit tests for echo command - all scenarios in one focused file"""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_basic_text(self, mock_get_backend, context):
        """Test basic echo with simple text"""
        fixture = load_coreutils_output("echo", "tier0_f549d2ca8e")  # echo without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="hello world")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_no_newline(self, mock_get_backend, context):
        """Test echo -n without trailing newline"""
        fixture = load_coreutils_output("echo", "tier0_e829ed4385")  # echo -n
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"]}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="hello world").with_option("-n")
        result = cmd.execute(context)

        assert result.success
        assert not result.raw_output.endswith("\n")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_escape_sequences(self, mock_get_backend, context):
        """Test echo -e with escape sequence interpretation"""
        fixture = load_coreutils_output("echo", "tier0_fb30c79bd2")  # echo -e
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="hello\\tworld").with_option("-e")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_multiple_words(self, mock_get_backend, context):
        """Test echo with multiple words and spaces"""
        fixture = load_coreutils_output("echo", "tier0_f549d2ca8e")  # echo without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="this is a test message")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_special_characters(self, mock_get_backend, context):
        """Test echo with special characters"""
        fixture = load_coreutils_output("echo", "tier0_f549d2ca8e")  # echo without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="!@#$%^&*()")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_empty_string(self, mock_get_backend, context):
        """Test echo with empty string"""
        fixture = load_coreutils_output("echo", "tier0_f549d2ca8e")  # echo without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_quotes_in_message(self, mock_get_backend, context):
        """Test echo with quotes in the message"""
        fixture = load_coreutils_output("echo", "tier0_f549d2ca8e")  # echo without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message='he said "hello"')
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_newlines_in_message(self, mock_get_backend, context):
        """Test echo with newlines in message"""
        fixture = load_coreutils_output("echo", "tier0_f549d2ca8e")  # echo without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="line1\\nline2")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_newlines_interpreted(self, mock_get_backend, context):
        """Test echo -e with interpreted newlines"""
        fixture = load_coreutils_output("echo", "tier0_fb30c79bd2")  # echo -e
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="line1\\nline2").with_option("-e")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_backslash_escapes(self, mock_get_backend, context):
        """Test echo -e with backslash escape sequences"""
        fixture = load_coreutils_output("echo", "tier0_fb30c79bd2")  # echo -e
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="path\\\\to\\\\file").with_option("-e")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_invalid_option(self, mock_get_backend, context):
        """Test echo with invalid option"""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=1,
            error_message="echo: invalid option -- 'z'",
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="test").with_option("-z")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "invalid option" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_echo_long_message(self, mock_get_backend, context):
        """Test echo with very long message"""
        fixture = load_coreutils_output("echo", "tier0_f549d2ca8e")  # echo without options
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=fixture["result"]["stdout"],
            success=fixture["result"]["exit_code"] == 0,
            structured_output=[{"text": fixture["result"]["stdout"].rstrip("\n")}],
            exit_code=fixture["result"]["exit_code"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = EchoCommand(message="a" * 1000)
        result = cmd.execute(context)

        assert result.success
