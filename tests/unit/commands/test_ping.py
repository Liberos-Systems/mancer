"""
Unit tests for ping command - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.network.ping_command import PingCommand


class TestPingCommand:
    """Unit tests for PingCommand - network connectivity testing."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ping_basic(self, mock_get_backend, context):
        """Test basic ping command."""
        ping_output = (
            "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n"
            "64 bytes from 8.8.8.8: icmp_seq=1 ttl=64 time=10.5 ms\n"
        )
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=ping_output,
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = PingCommand().host("8.8.8.8")
        result = cmd.execute(context)

        assert result.success
        assert "8.8.8.8" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ping_count(self, mock_get_backend, context):
        """Test ping -c count option."""
        ping_output = (
            "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n"
            "64 bytes from 8.8.8.8: icmp_seq=1 ttl=64 time=10.5 ms\n"
        )
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output=ping_output,
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = PingCommand().count(4).host("8.8.8.8")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-c" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ping_interval(self, mock_get_backend, context):
        """Test ping -i interval option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = PingCommand().interval(2.0).host("8.8.8.8")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-i" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ping_timeout(self, mock_get_backend, context):
        """Test ping -W timeout option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = PingCommand().timeout(5).host("8.8.8.8")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-W" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ping_failure(self, mock_get_backend, context):
        """Test ping with failure (host unreachable)."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=False,
            structured_output=[],
            exit_code=1,
            error_message="ping: unreachable: Name or service not known",
        )
        mock_get_backend.return_value = mock_backend

        cmd = PingCommand().host("unreachable.local")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "unreachable" in result.error_message
