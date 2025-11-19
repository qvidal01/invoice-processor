"""Security utilities."""

import hashlib
import re
from pathlib import Path
from typing import Union


def hash_content(content: Union[str, bytes]) -> str:
    """
    Generate SHA-256 hash of content.

    Args:
        content: String or bytes to hash

    Returns:
        Hex digest of hash
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    return hashlib.sha256(content).hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name

    # Remove non-alphanumeric characters (except dots, hyphens, underscores)
    filename = re.sub(r"[^\w\-.]", "_", filename)

    # Prevent empty or hidden files
    if not filename or filename.startswith("."):
        filename = "file_" + filename

    return filename


def validate_file_path(file_path: Path, allowed_directory: Path) -> bool:
    """
    Validate that file path is within allowed directory.

    Args:
        file_path: File path to validate
        allowed_directory: Allowed base directory

    Returns:
        True if path is safe
    """
    try:
        file_path.resolve().relative_to(allowed_directory.resolve())
        return True
    except ValueError:
        return False
