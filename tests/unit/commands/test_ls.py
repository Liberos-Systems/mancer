"""Unit tests for ls command."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import polars as pl

from mancer.infrastructure.command.file.ls_command import LsCommand
from tests.fixtures.loader import load_coreutils_output


class TestLsCommand:
    """Unit tests for LsCommand - file listing."""

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_basic_listing(self, mock_get_backend, context):
        """Test basic ls command without options."""
        fixture = load_coreutils_output("ls", "tier0_ebfdec6415")  # ls without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand()
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0
        assert cmd.build_command() == "ls"
        mock_backend.execute.assert_called_once()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_long_format(self, mock_get_backend, context):
        """Test ls -l with detailed output."""
        fixture = load_coreutils_output("ls", "tier1_64ee28f1ca")  # ls -l with directory
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_option("-l")
        result = cmd.execute(context)

        assert result.success
        assert "-l" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_all_files(self, mock_get_backend, context):
        """Test ls -a showing hidden files."""
        fixture = load_coreutils_output("ls", "tier0_abfc33352e")  # ls -a with directory
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_option("-a")
        result = cmd.execute(context)

        assert result.success
        assert "-a" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_custom_directory(self, mock_get_backend, context):
        """Test ls with custom directory path via add_arg."""
        fixture = load_coreutils_output("ls", "tier0_1e132fe99d")  # ls with directory
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().add_arg("/tmp/test_dir")
        result = cmd.execute(context)

        assert result.success
        assert "/tmp/test_dir" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_human_readable(self, mock_get_backend, context):
        """Test ls -lh with human readable sizes."""
        fixture = load_coreutils_output("ls", "tier1_2c264089f7")  # ls -l -h with directory
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_option("-l").with_option("-h")
        result = cmd.execute(context)

        assert result.success
        assert "-l" in cmd.build_command() and "-h" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_nonexistent_directory(self, mock_get_backend, context):
        """Test ls with non-existent directory."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            2,
            "",
            "ls: cannot access '/nonexistent': No such file or directory",
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().add_arg("/nonexistent")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 2
        assert "No such file or directory" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_permission_denied(self, mock_get_backend, context):
        """Test ls with permission denied."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            2,
            "",
            "ls: cannot open directory '/root': Permission denied",
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().add_arg("/root")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 2
        assert "Permission denied" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_invalid_option(self, mock_get_backend, context):
        """Test ls with invalid option."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (2, "", "ls: invalid option -- 'z'")
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_option("-z")
        result = cmd.execute(context)

        assert not result.success
        assert result.exit_code == 2
        assert "invalid option" in result.error_message

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_empty_directory(self, mock_get_backend, context):
        """Test ls on empty directory."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (0, "", "")
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().add_arg("/tmp/empty")
        result = cmd.execute(context)

        assert result.success
        assert result.exit_code == 0
        assert result.raw_output == ""

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_with_time_sorting(self, mock_get_backend, context):
        """Test ls -t sorting by modification time."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (0, "newer_file.txt\nolder_file.txt\n", "")
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_option("-t")
        result = cmd.execute(context)

        assert result.success
        assert "-t" in cmd.build_command()

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_structured_output_parsing(self, mock_get_backend, context):
        """Test that ls -l parses output into structured DataFrame."""
        fixture = load_coreutils_output("ls", "tier1_64ee28f1ca")  # ls -l with directory
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_option("-l")
        result = cmd.execute(context)

        assert result.success
        structured = result.structured_output
        assert isinstance(structured, pl.DataFrame)
        assert len(structured) > 0
        # Check that structured output has expected columns
        assert "name" in structured.columns
        assert "permissions" in structured.columns

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_with_sudo(self, mock_get_backend, context):
        """Test ls with sudo prefix."""
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (0, "root_file.txt\n", "")
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_sudo().add_arg("/root")
        result = cmd.execute(context)

        assert result.success
        assert cmd.build_command().startswith("sudo ls")

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_multiple_options_chained(self, mock_get_backend, context):
        """Test ls with multiple options chained together."""
        fixture = load_coreutils_output("ls", "tier1_26eb1d2452")  # ls -l -a with directory
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand().with_option("-l").with_option("-a").with_option("-h").with_option("-t")
        result = cmd.execute(context)

        assert result.success
        built = cmd.build_command()
        assert "-l" in built
        assert "-a" in built
        assert "-h" in built
        assert "-t" in built


class TestLsBuilderMethods:
    """Tests for LsCommand builder methods."""

    def test_all_method_adds_a_option(self):
        """all() adds -a option."""
        cmd = LsCommand().all()
        assert "-a" in cmd.build_command()

    def test_long_method_adds_l_option(self):
        """long() adds -l option."""
        cmd = LsCommand().long()
        assert "-l" in cmd.build_command()

    def test_human_readable_method_adds_h_option(self):
        """human_readable() adds -h option."""
        cmd = LsCommand().human_readable()
        assert "-h" in cmd.build_command()

    def test_sort_by_size_adds_S_option(self):
        """sort_by_size() adds -S option."""
        cmd = LsCommand().sort_by_size()
        assert "-S" in cmd.build_command()

    def test_sort_by_time_adds_t_option(self):
        """sort_by_time() adds -t option."""
        cmd = LsCommand().sort_by_time()
        assert "-t" in cmd.build_command()

    def test_in_directory_sets_path_parameter(self):
        """in_directory() sets path parameter."""
        cmd = LsCommand().in_directory("/var/log")
        assert "/var/log" in cmd.build_command()

    def test_builder_methods_can_be_chained(self):
        """Multiple builder methods can be chained."""
        cmd = LsCommand().long().all().human_readable().sort_by_time()
        built = cmd.build_command()
        assert "-l" in built
        assert "-a" in built
        assert "-h" in built
        assert "-t" in built

    def test_builder_returns_new_instance(self):
        """Builder methods return new instance (immutable)."""
        original = LsCommand()
        modified = original.long()

        assert original is not modified
        assert "-l" not in original.build_command()
        assert "-l" in modified.build_command()


class TestLsCommandPiping:
    """Tests for ls command with piped input."""

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_pipe_to_grep(self, mock_get_backend, context, result_factory):
        """ls can pipe output to next command."""
        fixture = load_coreutils_output("ls", "tier0_ebfdec6415")  # ls without options
        mock_backend = MagicMock()
        mock_backend.execute.return_value = (
            fixture["result"]["exit_code"],
            fixture["result"]["stdout"],
            fixture["result"]["stderr"],
        )
        mock_get_backend.return_value = mock_backend

        cmd = LsCommand()
        result = cmd.execute(context)

        # Result can be used as input for next command
        assert result.success
        assert result.raw_output  # Has output to pipe

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_then_creates_chain(self, mock_get_backend, context):
        """ls.then() creates CommandChain."""
        from mancer.domain.service.command_chain_service import CommandChain
        from mancer.infrastructure.command.file.grep_command import GrepCommand

        ls = LsCommand()
        grep = GrepCommand().pattern("txt")
        chain = ls.then(grep)

        assert isinstance(chain, CommandChain)

    @patch("mancer.infrastructure.command.base_command.BaseCommand._get_backend")
    def test_ls_pipe_creates_pipeline_chain(self, mock_get_backend, context):
        """ls.pipe() creates pipeline CommandChain."""
        from mancer.domain.service.command_chain_service import CommandChain
        from mancer.infrastructure.command.file.grep_command import GrepCommand

        ls = LsCommand()
        grep = GrepCommand().pattern("txt")
        chain = ls.pipe(grep)

        assert isinstance(chain, CommandChain)
        assert chain.is_pipeline[1] is True
