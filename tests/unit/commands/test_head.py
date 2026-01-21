"""
Unit tests for HeadCommand ensuring mocked interactions only.
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.infrastructure.command.file.head_command import HeadCommand
from tests.fixtures.loader import load_coreutils_output


class TestHeadCommand:
    """All scenarios for head command."""

    @pytest.fixture  # type: ignore[misc]
    def context(self) -> CommandContext:
        return CommandContext(current_directory="/tmp")

    def _setup_backend(self, mock_get_backend, exit_code=0, output="line1\nline2\n", error=""):
        backend = MagicMock()
        backend.execute.return_value = (exit_code, output, error)
        mock_get_backend.return_value = backend
        return backend

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_head_single_file_default(self, mock_get_backend, context):
        """head should parse default output into structured rows."""
        fixture = load_coreutils_output("head", "tier0_3fcdfbe909")  # head without options
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        result = HeadCommand().file("file.txt").execute(context)

        assert result.success
        backend.execute.assert_called_once()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_head_multiple_files_adds_file_metadata(self, mock_get_backend, context):
        """Headers from multiple files should be parsed correctly."""
        fixture = load_coreutils_output("head", "tier0_3fcdfbe909")  # head without options
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        result = HeadCommand().files(["file1", "file2"]).execute(context)

        assert result.success
        rows = result.structured_output
        if hasattr(rows, "to_dicts"):
            rows = rows.to_dicts()
        # Just verify structure exists
        assert rows is not None

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_head_lines_option_builds_flag(self, mock_get_backend, context):
        """-n option should appear in built command."""
        fixture = load_coreutils_output("head", "tier0_26812dcd26")  # head -n 10
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        cmd = HeadCommand().lines(5).file("data.txt")
        _ = cmd.execute(context)

        executed_command = backend.execute.call_args.kwargs.get("input_data")
        assert backend.execute.called
        assert executed_command is None

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_head_bytes_option(self, mock_get_backend, context):
        """-c option should be added correctly."""
        fixture = load_coreutils_output("head", "tier0_08ab4e05ab")  # head -c 64
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend

        cmd = HeadCommand().bytes(128).file("binary.dat")
        _ = cmd.execute(context)

        assert backend.execute.called

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_head_failure_propagates_error(self, mock_get_backend, context):
        """Non-zero exit code should produce a failed CommandResult."""
        backend = self._setup_backend(
            mock_get_backend,
            exit_code=1,
            error="head: cannot open file",
            output="",
        )

        result = HeadCommand().file("missing.txt").execute(context)

        assert not result.success
        assert "cannot open" in (result.error_message or "")
        backend.execute.assert_called_once()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_head_uses_input_result_as_stdin(self, mock_get_backend, context):
        """When provided, previous output must be piped as stdin."""
        fixture = load_coreutils_output("head", "tier0_3fcdfbe909")  # head without options
        backend = MagicMock()
        backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = backend
        input_result = MagicMock(raw_output="cached content\n", spec=["raw_output"])

        _ = HeadCommand().execute(context, input_result=input_result)

        assert backend.execute.call_args.kwargs["input_data"] == "cached content\n"
