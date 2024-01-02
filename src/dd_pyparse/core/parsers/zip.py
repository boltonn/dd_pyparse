import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile, ZipInfo

from dd_pyparse.core.parsers.base import FileStreamer
from dd_pyparse.schemas.data.parents.file import File


class ZipParser(FileStreamer):
    @staticmethod
    def standardize_file_meta(info: ZipInfo):
        """Standardize the file meta"""
        date_modified = info.date_time
        file_sub_path = info.filename
        file_name = os.path.basename(file_sub_path) if file_sub_path else None

        return {
            "date_modified": datetime(*date_modified) if date_modified else None,
            "file_extension": Path(file_name).suffix if file_name else None,
            "file_name": file_name,
            "file_size": info.file_size,
            "file_uri": file_sub_path,
        }

    @staticmethod
    def extract(
        info: ZipInfo,
        archive: ZipFile,
        extract_children: bool = False,
        out_dir: Path = None,
        password: str = None,
        password_encoding: str = "utf-8",
    ) -> File:
        password = bytes(password, encoding=password_encoding) if isinstance(password, str) else password
        child = ZipParser.standardize_file_meta(info)
        if extract_children:
            out_path = out_dir / child["file_uri"]
            archive.extract(info, path=out_dir, pwd=password)
            child["absolute_path"] = out_path.absolute()
        return File(**child)

    @staticmethod
    def stream(
        file_path: Path | BytesIO,
        extract_children: bool = False,
        num_threads: int = 4,
        out_dir: Path = None,
        **kwargs,
    ) -> Iterator[File]:
        """Stream a zip file"""
        # create  an extract function with set parameters
        with ZipFile(file_path, mode="r") as archive:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [
                    executor.submit(
                        lambda info: ZipParser.extract(info, archive=archive, extract_children=extract_children, out_dir=out_dir, **kwargs),
                        info,
                    )
                    for info in archive.infolist()
                    if info.is_dir() is False
                ]
        for future in futures:
            child = future.result()
            if child.absolute_path.is_file():
                yield child
