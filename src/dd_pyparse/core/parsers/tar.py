from datetime import datetime
from pathlib import Path
from tarfile import TarFile, TarInfo
from typing import Iterator

from dd_pyparse.core.parsers.base import FileStreamer
from dd_pyparse.core.utils.general import get_hashes, safe_open
from dd_pyparse.schemas.data.parents.file import File


class TarParser(FileStreamer):
    @staticmethod
    def standardize_file_meta(info: TarInfo):
        """Standardize the file meta"""
        info = info.get_info()
        date_modified = info.get("mtime")
        file_sub_path = Path(info.get("name"))
        file_name = file_sub_path.name if file_sub_path else None

        return {
            "date_modified": datetime.fromtimestamp(date_modified) if date_modified else None,
            "file_extension": Path(file_name).suffix,
            "file_name": file_name,
            "file_size": info.get("size"),
            "file_uri": str(file_sub_path),
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
                    with archive.extractfile(member) as fb:
                        child["hash"] = get_hashes(fb)
                        out_file_name = child["hash"]["md5"] + child.get("file_extension", ".bin")
                        out_path = out_dir / out_file_name
                        with safe_open(out_path, "wb") as out:
                            out.write(fb.read())
                    # archive.extract(member, path=out_dir)
                    child["absolute_path"] = out_path.absolute()
                yield File(**child)
        archive.close()
