import gzip
from pathlib import Path

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.utils.general import get_hashes, safe_open
from dd_pyparse.schemas.data.parents.file import File

# Note: Gzip is a file compression format, not an archive format so inferits the FileParser class


class GzipParser(FileParser):
    """Gzip file parser"""

    @staticmethod
    def parse(
        file: Path | bytes,
        file_name: str = None,
        extract_children: bool = False,
        out_dir: Path = None,
        **kwargs,
    ):
        """Parse a gzip file"""
        out = {}
        if isinstance(file, bytes):
            out_file_name = get_hashes(file)["md5"] if file_name is None else file_name
            if extract_children:
                out_path = out_dir / out_file_name
                with safe_open(out_path, "wb") as fb:
                    fb.write(gzip.decompress(file))
                out["absolute_path"] = out_path

        elif isinstance(file, (str, Path)):
            file = Path(file)
            out_file_name = Path(file.name.removesuffix(".gz"))
            if extract_children:
                with gzip.open(file, "rb") as fb:
                    out = {
                        "hash": get_hashes(fb),
                        "file_name": str(out_file_name),
                        "file_extension": out_file_name.suffix,                      
                    }
                    out_file_name = out["hash"]["md5"] + out.get("file_extension", ".bin")
                    out_path = out_dir / out_file_name
                    with safe_open(out_path, "wb") as fb_out:
                        fb_out.write(fb.read())
                out["absolute_path"] = out_path
                out = File(**out)
        return {"children": [out]}
