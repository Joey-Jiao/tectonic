import pytest
from pathlib import Path
from unittest.mock import patch

from tectonic.commands.dotfiles import get_dotfile_mappings, file_diff


class TestGetDotfileMappings:
    def test_returns_list(self):
        mappings = get_dotfile_mappings()
        assert isinstance(mappings, list)

    def test_mappings_are_tuples(self):
        mappings = get_dotfile_mappings()
        for mapping in mappings:
            assert isinstance(mapping, tuple)
            assert len(mapping) == 2
            assert isinstance(mapping[0], Path)
            assert isinstance(mapping[1], Path)

    def test_source_files_exist(self):
        mappings = get_dotfile_mappings()
        for src, dst in mappings:
            assert src.exists(), f"Source file not found: {src}"


class TestFileDiff:
    def test_diff_identical_files(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("same content\n")
        file2.write_text("same content\n")

        result = file_diff(file1, file2)

        assert result == []

    def test_diff_different_files(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("line 1\nline 2\n")
        file2.write_text("line 1\nchanged line\n")

        result = file_diff(file1, file2)

        assert result is not None
        assert len(result) > 0
        # Should contain diff markers
        diff_text = "".join(result)
        assert "-changed line" in diff_text or "+line 2" in diff_text

    def test_diff_nonexistent_source(self, tmp_path):
        src = tmp_path / "nonexistent.txt"
        dst = tmp_path / "existing.txt"
        dst.write_text("content")

        result = file_diff(src, dst)

        assert result is not None
        assert "Source not found" in result[0]

    def test_diff_nonexistent_destination(self, tmp_path):
        src = tmp_path / "existing.txt"
        src.write_text("content")
        dst = tmp_path / "nonexistent.txt"

        result = file_diff(src, dst)

        assert result is not None
        assert "Destination not found" in result[0]

    def test_diff_binary_file_returns_none(self, tmp_path):
        file1 = tmp_path / "file1.bin"
        file2 = tmp_path / "file2.bin"
        file1.write_bytes(b"\x00\x01\x02\xff")
        file2.write_bytes(b"\x00\x01\x03\xff")

        result = file_diff(file1, file2)

        assert result is None


class TestDotfilesIntegration:
    """Integration tests using CLI runner."""

    def test_status_command(self):
        from typer.testing import CliRunner
        from tectonic.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["dotfiles", "status"])

        # Should not crash
        assert result.exit_code == 0

    def test_diff_command(self):
        from typer.testing import CliRunner
        from tectonic.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["dotfiles", "diff"])

        # Should not crash
        assert result.exit_code == 0
