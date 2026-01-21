"""
Unit tests for wc command - all scenarios in one focused file
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.infrastructure.command.system.wc_command import WcCommand
from tests.fixtures.loader import load_coreutils_output


class TestWcCommand:
    """Unit tests for wc command - all scenarios in one focused file"""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_basic_count(self, mock_get_backend, context):
        """Test basic wc showing all counts (lines, words, characters)"""
        fixture = load_coreutils_output("wc", "tier0_7e284c5797")  # wc without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_lines_only(self, mock_get_backend, context):
        """Test wc -l counting only lines"""
        fixture = load_coreutils_output("wc", "tier0_70fbc1cb9c")  # wc -l
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt").with_option("-l")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_words_only(self, mock_get_backend, context):
        """Test wc -w counting only words"""
        fixture = load_coreutils_output("wc", "tier1_03ea95e03f")  # wc -w
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt").with_option("-w")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_characters_only(self, mock_get_backend, context):
        """Test wc -c counting only characters"""
        fixture = load_coreutils_output("wc", "tier0_8b57ee68c2")  # wc -c
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt").with_option("-c")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_bytes_only(self, mock_get_backend, context):
        """Test wc -m counting bytes (same as characters in ASCII)"""
        fixture = load_coreutils_output("wc", "tier0_c8308baecb")  # wc -m
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt").with_option("-m")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_longest_line(self, mock_get_backend, context):
        """Test wc -L finding longest line length"""
        fixture = load_coreutils_output("wc", "tier0_7b57517060")  # wc -L
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt").with_option("-L")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_multiple_files(self, mock_get_backend, context):
        """Test wc with multiple files"""
        fixture = load_coreutils_output("wc", "tier0_7e284c5797")  # wc without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file1.txt", "file2.txt")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_stdin_input(self, mock_get_backend, context):
        """Test wc reading from stdin (no filename)"""
        fixture = load_coreutils_output("wc", "tier0_7e284c5797")  # wc without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand()  # No filename = read from stdin
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_empty_file(self, mock_get_backend, context):
        """Test wc with empty file"""
        fixture = load_coreutils_output("wc", "tier0_7e284c5797")  # wc without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("empty.txt")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_file_not_found(self, mock_get_backend, context):
        """Test wc with non-existent file"""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (1, "", "wc: nonexistent.txt: No such file or directory")
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("nonexistent.txt")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "No such file or directory" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_permission_denied(self, mock_get_backend, context):
        """Test wc with permission denied"""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (1, "", "wc: /etc/shadow: Permission denied")
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("/etc/shadow")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "Permission denied" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_invalid_option(self, mock_get_backend, context):
        """Test wc with invalid option"""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (1, "", "wc: invalid option -- 'z'")
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt").with_option("-z")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "invalid option" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_wc_combined_options(self, mock_get_backend, context):
        """Test wc with combined options"""
        fixture = load_coreutils_output("wc", "tier0_70fbc1cb9c")  # wc -l
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = WcCommand("file.txt").with_option("-l").with_option("-w")
        result = cmd.execute(context)

        assert result.success
