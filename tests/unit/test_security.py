"""Tests for security utilities."""

from pathlib import Path

from invoice_processor.utils.security import (
    hash_content,
    sanitize_filename,
    validate_file_path,
)


class TestHashContent:
    """Tests for hash_content function."""

    def test_hash_string_content(self) -> None:
        """Test hashing string content."""
        content = "test content"
        hash1 = hash_content(content)
        hash2 = hash_content(content)

        # Same content should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters

    def test_hash_bytes_content(self) -> None:
        """Test hashing bytes content."""
        content = b"test content"
        hash_result = hash_content(content)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64

    def test_different_content_different_hash(self) -> None:
        """Test that different content produces different hashes."""
        hash1 = hash_content("content 1")
        hash2 = hash_content("content 2")

        assert hash1 != hash2


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_clean_filename(self) -> None:
        """Test that clean filenames pass through unchanged."""
        filename = "invoice_2024_01.pdf"
        result = sanitize_filename(filename)

        assert result == filename

    def test_remove_path_components(self) -> None:
        """Test that path components are removed."""
        filename = "../../etc/passwd"
        result = sanitize_filename(filename)

        assert result == "passwd"
        assert "/" not in result
        assert ".." not in result

    def test_remove_special_characters(self) -> None:
        """Test that special characters are replaced."""
        filename = "invoice@#$%.pdf"
        result = sanitize_filename(filename)

        # Should only contain alphanumeric, dots, hyphens, underscores
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
        assert "%" not in result

    def test_prevent_hidden_files(self) -> None:
        """Test that hidden files get prefixed."""
        filename = ".hidden"
        result = sanitize_filename(filename)

        assert result.startswith("file_")

    def test_preserve_extension(self) -> None:
        """Test that file extensions are preserved."""
        filename = "my invoice.pdf"
        result = sanitize_filename(filename)

        assert result.endswith(".pdf")


class TestValidateFilePath:
    """Tests for validate_file_path function."""

    def test_valid_path_within_directory(self, tmp_path: Path) -> None:
        """Test that valid path within allowed directory passes."""
        allowed_dir = tmp_path / "allowed"
        allowed_dir.mkdir()

        file_path = allowed_dir / "invoice.pdf"

        assert validate_file_path(file_path, allowed_dir) is True

    def test_invalid_path_outside_directory(self, tmp_path: Path) -> None:
        """Test that path outside allowed directory fails."""
        allowed_dir = tmp_path / "allowed"
        allowed_dir.mkdir()

        file_path = tmp_path / "outside" / "invoice.pdf"

        assert validate_file_path(file_path, allowed_dir) is False

    def test_path_traversal_attempt(self, tmp_path: Path) -> None:
        """Test that path traversal attempts are blocked."""
        allowed_dir = tmp_path / "allowed"
        allowed_dir.mkdir()

        file_path = allowed_dir / ".." / ".." / "etc" / "passwd"

        assert validate_file_path(file_path, allowed_dir) is False
