import pytest


@pytest.fixture
def sample_files(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    text_file = src_dir / "test.txt"
    text_file.write_text("hello world")

    bin_file = src_dir / "test.bin"
    bin_file.write_bytes(b"\x00\x01\x02\x03")

    nested_dir = src_dir / "nested"
    nested_dir.mkdir()
    nested_file = nested_dir / "nested.txt"
    nested_file.write_text("nested content")

    dst_dir = tmp_path / "dst"
    dst_dir.mkdir()

    return {
        "src_dir": src_dir,
        "dst_dir": dst_dir,
        "text_file": text_file,
        "bin_file": bin_file,
        "nested_dir": nested_dir,
        "nested_file": nested_file,
    }
