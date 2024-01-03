import subprocess
from pathlib import Path
from typing import Iterator

from loguru import logger
from py7zr import SevenZipFile
from py7zr.py7zr import ArchiveFile

from dd_pyparse.core.parsers.base import FileStreamer
from dd_pyparse.schemas.data.parents.file import File


class SevenZipParser(FileStreamer):
    @staticmethod
    def standardize_file_meta(info: ArchiveFile):
        """Standardize the file meta"""
        info = info.file_properties()
        date_created = info.get("creationtime")
        date_created = date_created.as_datetime() if date_created else None
        date_modified = info.get("lastwrittentime")
        date_modified = date_modified.as_datetime() if date_modified else None
        file_sub_path = Path(info.get("filename"))
        file_name = file_sub_path.name if file_sub_path else None

        return {
            "date_created": date_created,
            "date_modified": date_modified,
            "file_extension": Path(file_name).suffix,
            "file_name": file_name,
            "file_size": info.get("uncompressed"),
            "file_uri": str(file_sub_path),
        }

    @staticmethod
    def stream(
        file_path: Path,
        extract_children: bool = False,
        num_threads: int = 4,
        out_dir: Path = None,
        password: str = None,
        **kwargs,
    ) -> Iterator[File]:
        """Stream a 7z file"""
        if not isinstance(file_path, Path):
            raise TypeError(f"Cannot parse {type(file_path)}")

        if extract_children:
            _call = ["7z", "e", str(file_path), f"-o{out_dir}", f"-mmt{num_threads}"]
            if password:
                _call.append(f"-p{password}")
            subprocess.call(_call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        archive = SevenZipFile(file_path, mode="r", password=password)
        for member in archive.files:
            if member.is_directory is False:
                try:
                    child = SevenZipParser.standardize_file_meta(member)
                    if extract_children:
                        out_path = out_dir / child["file_uri"]
                        child["absolute_path"] = out_path.absolute()
                    yield File(**child)
                except Exception as e:
                    logger.warning(f"Failed to parse {member.filename}: {e}")
        archive.close()
