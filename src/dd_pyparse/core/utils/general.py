import os
from hashlib import md5, sha256, sha512
from io import BufferedIOBase, BytesIO
from pathlib import Path
from typing import IO, Literal

from loguru import logger

from dd_pyparse.schemas.enums import HashType


def get_buffer_size(file: BytesIO) -> int:
    """Get the size of the buffer"""
    file.seek(0, os.SEEK_END)
    buffer_size = file.tell()
    file.seek(0)
    return buffer_size


def get_encoding_families(encoding: str) -> list[str]:
    """Get the encoding families of an encoding"""
    families: dict[str, list[str]] = {
        "rus": ["cp1251", "cp866", "iso8859_5", "koi8_r", "mac_cyrillic"],
        "zho": ["gb2312", "gbk", "gb18030"],
    }
    for _, encodings in families.items():
        if encoding in encodings:
            return encodings


def get_hashes(file: Path | bytes | BytesIO, byte_size: int = 1024) -> dict[HashType, str]:
    """Get the hashes of a file"""

    _md5 = md5()
    _sha256 = sha256()
    _sha512 = sha512()

    if isinstance(file, Path):
        with open(file, "rb") as fb:
            return get_hashes(fb, byte_size=byte_size)
    elif isinstance(file, bytes):
        _md5.update(file)
        _sha256.update(file)
        _sha512.update(file)
    elif isinstance(file, (BufferedIOBase, BytesIO)):
        while True:
            data = file.read(byte_size)
            if not data:
                break
            _md5.update(data)
            _sha256.update(data)
            _sha512.update(data)
    else:
        raise TypeError(f"Cannot get hashes for {type(file)}")

    return {
        "md5": _md5.hexdigest(),
        "sha256": _sha256.hexdigest(),
        "sha512": _sha512.hexdigest(),
    }


def get_leading_character(buffer: bytes, encoding: str = "utf-8") -> str:
    """Get the leading character of a file"""
    leading_char = buffer.read(1).decode(encoding=encoding)
    buffer.seek(0)
    return leading_char


def get_n_from_file(file: IO, n: int) -> bytes:
    """Get the first n bytes from a file"""
    if n>=0:
        file.seek(0)
        file_bytes = file.read(n)
        file.seek(0)
    else:
        file.seek(n, os.SEEK_END)
        file_bytes = file.read()
        file.seek(0)
    return file_bytes


def map_unsupported_encoding(encoding: str) -> str:
    """Map unsupported encodings to supported encodings"""
    mapping = {
        "x-gbk": "gbk",
    }
    return mapping.get(encoding, None)


def safe_open(file_path: Path, mode: Literal["w", "wb"]):
    """A utility function to create parent directories if they don't exist"""
    if not file_path.parent.exists():
        logger.debug(f"Creating parent directories for {file_path}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
    return open(file_path, mode)
