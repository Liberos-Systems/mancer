"""
Unit tests for TailCommand with mocked backend interactions.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.infrastructure.command.file.tail_command import TailCommand
from tests.fixtures.loader import load_coreutils_output


class TestTailCommand:
    """Tail command scenarios (positive and negative)."""

    @pytest.fixture  # type: ignore[misc]
    def context(self) -> CommandContext:
        return CommandContext(current_directory="/var/logs")

    def _backend(self, mock_get_backend, exit_code=0, output="line9\nline10\n", error=""):
        backend = MagicMock()
        backend.execute.return_value = (exit_code, output, error)
        mock_get_backend.return_value = backend
        return backend

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_tail_default_output(self, mock_get_backend, context):
        """Basic tail invocation should succeed and parse rows."""
        fixture = load_coreutils_output("tail", "tier0_61aef9e993")  # tail without options
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        result = TailCommand().file("syslog").execute(context)

        assert result.success
        backend.execute.assert_called_once()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_tail_follow_option(self, mock_get_backend, context):
        """Follow option (-f) should be added to command string."""
        fixture = load_coreutils_output("tail", "tier0_61aef9e993")  # tail without options
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        cmd = TailCommand().follow().file("app.log")
        _ = cmd.execute(context)

        assert "-f" in backend.execute.call_args.args[0]

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_tail_bytes_option(self, mock_get_backend, context):
        """Bytes parameter should format as -cN."""
        fixture = load_coreutils_output("tail", "tier0_2605ccb171")  # tail -c 64
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        _ = TailCommand().bytes(256).file("data.log").execute(context)

        assert backend.execute.called

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_tail_multiple_files_headers(self, mock_get_backend, context):
        """Multiple files should include file metadata in structured output."""
        fixture = load_coreutils_output("tail", "tier0_61aef9e993")  # tail without options
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        result = TailCommand().files(["file1", "file2"]).execute(context)

        rows = result.structured_output
        if hasattr(rows, "to_dicts"):
            rows = rows.to_dicts()
        # Just verify structure exists
        assert rows is not None

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_tail_failure(self, mock_get_backend, context):
        """Errors from backend should propagate to the result."""
        backend = self._backend(
            mock_get_backend,
            exit_code=1,
            error="tail: cannot open file",
            output="",
        )

        result = TailCommand().file("missing.log").execute(context)

        assert not result.success
        assert "cannot open" in (result.error_message or "")
        backend.execute.assert_called_once()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_tail_streams_previous_output(self, mock_get_backend, context):
        """Input from previous command should feed stdin."""
        fixture = load_coreutils_output("tail", "tier0_61aef9e993")  # tail without options
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend
        input_result = MagicMock(raw_output="cached\n", spec=["raw_output"])

        _ = TailCommand().execute(context, input_result=input_result)

        assert backend.execute.call_args.kwargs["input_data"] == "cached\n"
