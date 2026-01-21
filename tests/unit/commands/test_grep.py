"""Unit tests for grep command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from mancer.infrastructure.command.file.grep_command import GrepCommand
from tests.fixtures.loader import load_coreutils_output


class TestGrepCommand:
    """Unit tests for GrepCommand - pattern searching."""

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_basic_pattern_search(self, mock_get_backend, context):
        """Test basic grep pattern search."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("test").file("*.txt")
        result = cmd.execute(context)

        assert result.exit_code == fixture["result"]["exit_code"]
        mock_backend.execute.assert_called_once()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_case_insensitive(self, mock_get_backend, context):
        """Test grep -i case insensitive search."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("pattern").ignore_case()
        result = cmd.execute(context)

        assert "-i" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_line_numbers(self, mock_get_backend, context):
        """Test grep -n with line numbers."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("line").line_number()
        result = cmd.execute(context)

        assert "-n" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_invert_match(self, mock_get_backend, context):
        """Test grep -v invert match."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("pattern").invert_match()
        result = cmd.execute(context)

        assert "-v" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_recursive(self, mock_get_backend, context):
        """Test grep -r recursive search."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("match").recursive()
        result = cmd.execute(context)

        assert "-r" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_extended_regex(self, mock_get_backend, context):
        """Test grep -E extended regex."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("test[0-9]+").extended_regexp()
        result = cmd.execute(context)

        assert "-E" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_count_only(self, mock_get_backend, context):
        """Test grep -c count only mode."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("pattern").count()
        result = cmd.execute(context)

        assert "-c" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_no_matches_found(self, mock_get_backend, context):
        """Test grep when no matches are found (exit code 1)."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (1, "", "")
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("nonexistent")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_file_not_found(self, mock_get_backend, context):
        """Test grep with non-existent file."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            2,
            "",
            "grep: nonexistent.txt: No such file or directory",
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("pattern").file("nonexistent.txt")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 2
        assert "No such file or directory" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_structured_output_parsing(self, mock_get_backend, context):
        """Test that grep parses output into structured format."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = GrepCommand().pattern("match").line_number()
        result = cmd.execute(context)

        # Check structured output exists
        structured = result.structured_output
        # Handle both list and DataFrame cases
        if hasattr(structured, "to_dicts"):
            data = structured.to_dicts()
        else:
            data = list(structured) if structured else []
        # Just verify structure exists, don't check exact content
        assert structured is not None

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_grep_with_stdin_input(self, mock_get_backend, context, result_factory):
        """Test grep reading from stdin (piped input)."""
        fixture = load_coreutils_output("grep", "tier0_528b9e73e0")  # grep without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        input_result = result_factory(output="line1\nmatching line\nline3\n")
        cmd = GrepCommand().pattern("matching")
        result = cmd.execute(context, input_result=input_result)

        # Verify stdin was passed to backend
        call_args = mock_backend.execute.call_args
        assert call_args.kwargs.get("input_data") == "line1\nmatching line\nline3\n"
