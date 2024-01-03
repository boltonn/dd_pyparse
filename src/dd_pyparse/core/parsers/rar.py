from datetime import datetime
from pathlib import Path
from typing import Iterator

from rarfile import RarFile, RarInfo

from dd_pyparse.core.parsers.base import FileStreamer
from dd_pyparse.schemas.data.parents.file import File


class RarParser(FileStreamer):
    @staticmethod
    def standardize_file_meta(info: RarInfo):
        """Standardize the file meta"""
        file_sub_path = Path(info.filename)
        file_name = file_sub_path.name if file_sub_path else None
        date_modified = datetime.fromtimestamp(info.mtime) if info.mtime else None
        date_modified_os = datetime(*info.date_time) if info.date_time else None
        date_created = datetime.fromtimestamp(info.ctime) if info.ctime else None

        return {
            "date_created": date_created,
            "date_modified": date_modified or date_modified_os,
            "file_extension": Path(file_name).suffix,
            "file_name": file_name,
            "file_size": info.file_size,
            "file_uri": str(file_sub_path),
            # "system_os": info.file_host_os,
        }

    @staticmethod
    def stream(
        file_path: Path,
        extract_children: bool = False,
        out_dir: Path = None,
        password: str = None,
        **kwargs,
    ) -> Iterator[File]:
        """Stream a rar file"""
        if not isinstance(file_path, Path):
            raise TypeError(f"Cannot parse {type(file_path)}")

        archive = RarFile(file_path)
        for member in archive.infolist():
            if member.is_file():
                child = RarParser._standardize_file_meta(member)
                if extract_children:
                    out_path = out_dir / child["file_uri"]
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    archive.extract(member, path=out_path.parent, pwd=password)
                    child["absolute_path"] = out_path.absolute()
                yield File(**child)
