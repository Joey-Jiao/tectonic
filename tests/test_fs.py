from tectonic.core import fs


class TestEnsureDir:
    def test_creates_directory(self, tmp_path):
        new_dir = tmp_path / "new" / "nested" / "dir"
        assert not new_dir.exists()

        fs.ensure_dir(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_existing_directory_no_error(self, tmp_path):
        existing = tmp_path / "existing"
        existing.mkdir()

        # Should not raise
        fs.ensure_dir(existing)
        assert existing.exists()


class TestFilesEqual:
    def test_equal_text_files(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("same content")
        file2.write_text("same content")

        assert fs.files_equal(file1, file2)

    def test_different_text_files(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content A")
        file2.write_text("content B")

        assert not fs.files_equal(file1, file2)

    def test_equal_binary_files(self, tmp_path):
        file1 = tmp_path / "file1.bin"
        file2 = tmp_path / "file2.bin"
        file1.write_bytes(b"\x00\x01\x02")
        file2.write_bytes(b"\x00\x01\x02")

        assert fs.files_equal(file1, file2)

    def test_different_size_files(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("short")
        file2.write_text("much longer content")

        assert not fs.files_equal(file1, file2)


class TestCopy:
    def test_copy_new_file(self, sample_files):
        src = sample_files["text_file"]
        dst = sample_files["dst_dir"] / "copied.txt"

        fs.copy(src, dst)

        assert dst.exists()
        assert dst.read_text() == "hello world"

    def test_copy_overwrites_different_file(self, sample_files):
        src = sample_files["text_file"]
        dst = sample_files["dst_dir"] / "existing.txt"
        dst.write_text("old content")

        fs.copy(src, dst, do_backup=False)

        assert dst.read_text() == "hello world"

    def test_copy_skips_identical_file(self, sample_files, capsys):
        src = sample_files["text_file"]
        dst = sample_files["dst_dir"] / "same.txt"
        dst.write_text("hello world")

        fs.copy(src, dst)

        # File should still exist with same content
        assert dst.read_text() == "hello world"

    def test_copy_binary_file(self, sample_files):
        src = sample_files["bin_file"]
        dst = sample_files["dst_dir"] / "copied.bin"

        fs.copy(src, dst)

        assert dst.exists()
        assert dst.read_bytes() == b"\x00\x01\x02\x03"


class TestCopyDir:
    def test_copy_directory(self, sample_files):
        src = sample_files["src_dir"]
        dst = sample_files["dst_dir"] / "copied_src"

        fs.copy_dir(src, dst)

        assert dst.exists()
        assert (dst / "test.txt").read_text() == "hello world"
        assert (dst / "nested" / "nested.txt").read_text() == "nested content"

    def test_copy_dir_skips_existing(self, sample_files, capsys):
        src = sample_files["src_dir"]
        dst = sample_files["dst_dir"] / "existing"
        dst.mkdir()

        fs.copy_dir(src, dst)

        # Should not copy files into existing directory
        assert not (dst / "test.txt").exists()


class TestCopyTree:
    def test_copy_tree_merges(self, sample_files):
        src = sample_files["src_dir"]
        dst = sample_files["dst_dir"]

        # Create existing file in dst
        existing = dst / "existing.txt"
        existing.write_text("keep me")

        fs.copy_tree(src, dst, do_backup=False)

        # Original file should remain
        assert existing.read_text() == "keep me"
        # New files should be copied
        assert (dst / "test.txt").read_text() == "hello world"
        assert (dst / "nested" / "nested.txt").read_text() == "nested content"


class TestBackup:
    def test_backup_creates_copy(self, tmp_path):
        original = tmp_path / "original.txt"
        original.write_text("backup me")
        backup_dir = tmp_path / "backups"

        result = fs.backup(original, backup_dir)

        assert result is not None
        assert result.exists()
        assert result.read_text() == "backup me"
        assert backup_dir.exists()

    def test_backup_returns_none_for_nonexistent(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.txt"
        backup_dir = tmp_path / "backups"

        result = fs.backup(nonexistent, backup_dir)

        assert result is None

    def test_backup_returns_none_for_symlink(self, tmp_path):
        target = tmp_path / "target.txt"
        target.write_text("target")
        link = tmp_path / "link.txt"
        link.symlink_to(target)
        backup_dir = tmp_path / "backups"

        result = fs.backup(link, backup_dir)

        assert result is None


class TestSymlink:
    def test_create_symlink(self, tmp_path):
        src = tmp_path / "source.txt"
        src.write_text("source content")
        dst = tmp_path / "link.txt"

        fs.symlink(src, dst)

        assert dst.is_symlink()
        assert dst.read_text() == "source content"

    def test_symlink_replaces_existing_symlink(self, tmp_path):
        src1 = tmp_path / "source1.txt"
        src1.write_text("source 1")
        src2 = tmp_path / "source2.txt"
        src2.write_text("source 2")
        dst = tmp_path / "link.txt"
        dst.symlink_to(src1)

        fs.symlink(src2, dst)

        assert dst.is_symlink()
        assert dst.read_text() == "source 2"
