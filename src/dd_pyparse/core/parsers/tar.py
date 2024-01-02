import os
from datetime import datetime
from pathlib import Path
from tarfile import TarFile, TarInfo
from typing import Iterator

from dd_pyparse.core.parsers.base import FileStreamer
from dd_pyparse.schemas.data.parents.file import File


class TarParser(FileStreamer):
    @staticmethod
    def standardize_file_meta(info: TarInfo):
        """Standardize the file meta"""
        info = info.get_info()
        date_modified = info.get("mtime")
        file_sub_path = info.get("name")
        file_name = os.path.basename(file_sub_path)

        return {
            "date_modified": datetime.fromtimestamp(date_modified) if date_modified else None,
            "file_extension": Path(file_name).suffix if file_name else None,
            "file_name": os.path.basename(file_sub_path) if file_sub_path else None,
            "file_size": info.get("size"),
            "file_uri": file_sub_path,
        }

    @staticmethod
    def stream(
        file_path: Path,
        encoding: str = None,
        extract_children: bool = False,
        out_dir: Path = None,
        **kwargs,
    ) -> Iterator[File]:
        """Stream a tar file"""
        if not isinstance(file_path, Path):
            raise TypeError(f"Cannot parse {type(file_path)}")

        archive = TarFile(file_path, encoding=encoding)
        for member in archive.getmembers():
            if member.isfile():
                child = TarParser.standardize_file_meta(member)
                if extract_children:
                    out_path = out_dir / child["file_uri"]
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    archive.extract(member, path=out_dir)
                    child["absolute_path"] = out_path.absolute()
                yield File(**child)
        archive.close()
