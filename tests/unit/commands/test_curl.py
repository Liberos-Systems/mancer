"""
Unit tests for CurlCommand - non-invasive tests using mocks.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.domain.model.command_result import CommandResult
from mancer.infrastructure.command.network.curl_command import CurlCommand


class TestCurlCommand:
    """Unit tests for CurlCommand - HTTP client."""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext(current_directory="/tmp")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_curl_basic_get(self, mock_get_backend, context):
        """Test basic curl GET request."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="<html>...</html>",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = CurlCommand().url("https://example.com")
        result = cmd.execute(context)

        assert result.success
        assert "https://example.com" in mock_backend.execute_command.call_args[0][0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_curl_silent(self, mock_get_backend, context):
        """Test curl -s silent option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="<html>...</html>",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = CurlCommand().silent().url("https://example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-s" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_curl_verbose(self, mock_get_backend, context):
        """Test curl -v verbose option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="* Connected to example.com\n<html>...</html>",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = CurlCommand().verbose().url("https://example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-v" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_curl_output(self, mock_get_backend, context):
        """Test curl -o output option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = CurlCommand().output("file.html").url("https://example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-o" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_curl_header(self, mock_get_backend, context):
        """Test curl -H header option."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output="",
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = CurlCommand().header("Authorization: Bearer token").url("https://example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-H" in executed_command

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_curl_post(self, mock_get_backend, context):
        """Test curl POST request."""
        mock_backend = MagicMock()
        mock_backend.execute_command.return_value = CommandResult(
            raw_output='{"status": "ok"}',
            success=True,
            structured_output=[],
            exit_code=0,
        )
        mock_get_backend.return_value = mock_backend

        cmd = CurlCommand().method("POST").data('{"key": "value"}').url("https://api.example.com")
        result = cmd.execute(context)

        assert result.success
        executed_command = mock_backend.execute_command.call_args[0][0]
        assert "-X" in executed_command
        assert "-d" in executed_command
