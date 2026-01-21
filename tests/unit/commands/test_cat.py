"""
Unit tests for cat command - all scenarios in one focused file
"""

from unittest.mock import MagicMock, patch

import pytest

from mancer.domain.model.command_context import CommandContext
from mancer.infrastructure.command.system.cat_command import CatCommand
from tests.fixtures.loader import load_coreutils_output


class TestCatCommand:
    """Unit tests for cat command - all scenarios in one focused file"""

    @pytest.fixture
    def context(self):
        """Test command context fixture"""
        return CommandContext()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_single_file(self, mock_get_backend, context):
        """Test cat displaying single file content"""
        fixture = load_coreutils_output("cat", "tier0_eb97c208f5")  # cat without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="test.txt")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_multiple_files(self, mock_get_backend, context):
        """Test cat concatenating multiple files"""
        fixture = load_coreutils_output("cat", "tier0_eb97c208f5")  # cat without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="file1.txt").with_option("file2.txt")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_with_line_numbers(self, mock_get_backend, context):
        """Test cat -n with line numbers"""
        fixture = load_coreutils_output("cat", "tier0_b60ac41579")  # cat -n
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="test.txt").with_option("-n")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_show_nonprinting(self, mock_get_backend, context):
        """Test cat -v showing non-printing characters"""
        fixture = load_coreutils_output("cat", "tier0_c292a00d07")  # cat -A (show-all)
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="test.txt").with_option("-v")
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_squeeze_blank_lines(self, mock_get_backend, context):
        """Test cat -s squeezing blank lines"""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (0, "line1\n\nline2\n", "")
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="test.txt").with_option("-s")
        result = cmd.execute(context)

        assert result.success
        assert result.raw_output.count("\n\n") <= 1

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_file_not_found(self, mock_get_backend, context):
        """Test cat with non-existent file"""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (1, "", "cat: nonexistent.txt: No such file or directory")
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="nonexistent.txt")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "No such file or directory" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_permission_denied(self, mock_get_backend, context):
        """Test cat with permission denied"""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (1, "", "cat: /etc/shadow: Permission denied")
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="/etc/shadow")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 1
        assert "Permission denied" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_empty_file(self, mock_get_backend, context):
        """Test cat with empty file"""
        fixture = load_coreutils_output("cat", "tier0_eb97c208f5")  # cat without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="empty.txt")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_stdin_input(self, mock_get_backend, context):
        """Test cat reading from stdin"""
        fixture = load_coreutils_output("cat", "tier0_eb97c208f5")  # cat without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand()  # No file specified = read from stdin
        result = cmd.execute(context)

        assert result.success

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_cat_show_ends(self, mock_get_backend, context):
        """Test cat -E showing line ends"""
        fixture = load_coreutils_output("cat", "tier0_66ff06f3b3")  # cat -E
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = CatCommand(file_path="test.txt").with_option("-E")
        result = cmd.execute(context)

        assert result.success
