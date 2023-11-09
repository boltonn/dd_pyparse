from hashlib import md5, sha1, sha256
from pathlib import Path

import magic

from pyparse.schemas.data.parents.file import File


class FileParser:
    mime = magic.Magic(mime=True)

    @staticmethod
    def read_from_filesystem(filepath: Path, encoding:str = None) -> bytes:
        with open(filepath, "rb", encoding=encoding) as fb:
            file = fb.read()
        return file

    @staticmethod
    def get_mime_type(file: Path | bytes):
        if isinstance(file, bytes):
            return FileParser.mime.from_buffer(file)
        return FileParser.mime.from_file(str(file))

    @staticmethod
    def get_hashes(file: Path | bytes, byte_size: int = 1024) -> dict[str, str]:
        """ "Get MD5, SHA1, and SHA256 hashes of a file."""

        _md5 = md5()
        _sha1 = sha1()
        _sha256 = sha256()

        if isinstance(file, bytes):
            _md5.update(file)
            _sha1.update(file)
            _sha256.update(file)
        elif isinstance(file, Path):
            with open(file, "rb") as fb:
                while True:
                    data = fb.read(byte_size)
                    if not data:
                        break
                    _md5.update(data)
                    _sha1.update(data)
                    _sha256.update(data)

        return {
            "md5": str(_md5.hexdigest()),
            "sha1": str(_sha1.hexdigest()),
            "sha256": str(_sha256.hexdigest()),
        }

    @staticmethod
    def parse_bytes(file: bytes, byte_size: int = 1024) -> dict:
        return {
            "hashes": FileParser.get_hashes(file, byte_size=byte_size),
            "mime_type": FileParser.get_mime_type(file),
            "file_size": len(file),
        }

    @staticmethod
    def parse(file: Path | bytes, encoding=None) -> File:
        meta = {}
        if isinstance(file, str):
            file = Path(file)
            
        if isinstance(file, Path):
            meta |= {
                "file_path": file,
                "file_ext": file.suffix,
                "file_name": file.name,
                "date_modified": file.stat().st_mtime,
                "date_created": file.stat().st_ctime,
            }
            file = FileParser.read_from_filesystem(file)
        meta |= FileParser.parse_bytes(file)

        return meta
