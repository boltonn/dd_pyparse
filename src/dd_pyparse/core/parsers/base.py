from abc import abstractmethod
from datetime import datetime
from functools import singledispatch
from io import BytesIO
from pathlib import Path

from dd_pyparse.core.utils.filetype import get_extension, route_mime_type
from dd_pyparse.core.utils.general import get_hashes
from dd_pyparse.schemas.base import Base

@singledispatch
def get_file_meta(file, *args, **kwargs) -> dict:
    """Get metadata about the file"""
    raise NotImplementedError(f"Cannot get metadata for {type(file)}")


@get_file_meta.register(str)
@get_file_meta.register(Path)
def _(file, encoding: str = None) -> dict:
    """Get metadata about the file"""
    with open(file, "rb", encoding=encoding) as fb:
        mime_type, file_type = route_mime_type(file_name=file.name, file=fb)
    file_stat = file.stat()

    return {
        "absolute_path": file.absolute(),
        "date_modified": datetime.fromtimestamp(file_stat.st_mtime),
        "date_created": datetime.fromtimestamp(file_stat.st_ctime),
        "hash": get_hashes(file),
        "file_extension": file.suffix,
        "file_name": file.name,
        "file_size": file_stat.st_size,
        "file_type": file_type,
        "mime_type": mime_type,
    }


@get_file_meta.register(bytes)
def _(file) -> dict:
    """Get metadata about the file"""
    file_size = len(file)
    file = BytesIO(file)
    file.seek(0)
    mime_type, file_type = route_mime_type(file=file)

    return {
        "hash": get_hashes(file),
        "file_extension": get_extension(file),
        "file_size": file_size,
        "file_type": file_type,
        "mime_type": mime_type,
    }

try:
    from starlette.datastructures import UploadFile
    @get_file_meta.register(UploadFile)
    def _(file) -> dict:
        """Get metadata about the file"""
        mime_type = file.content_type
        file_name = Path(file.filename).name
        mime_type, file_type = route_mime_type(file_name=file.filename, file=file.file._file, mime_type=mime_type)
        file_stat = file.file.stat()

        return {
            "date_modified": datetime.fromtimestamp(file_stat.st_mtime),
            "date_created": datetime.fromtimestamp(file_stat.st_ctime),
            "hash": get_hashes(file.file._file),
            "file_extension": get_extension(file_name),
            "file_name": file_name,
            "file_size": file_stat.st_size,
            "file_type": file_type,
            "mime_type": mime_type,
        }
except ImportError:
    pass


class FileParser:
    @abstractmethod
    def parse(self, file: Path | bytes, **kwargs) -> Base:
        raise NotImplementedError


class FileStreamer:
    @abstractmethod
    def stream(self, file_path: Path, extract_children: bool = False, out_dir: Path = None, **kwargs) -> Base:
        raise NotImplementedError
