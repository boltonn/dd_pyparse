import json
from pathlib import Path

import ijson

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.utils.general import get_leading_character


class JsonParser(FileParser):
    """Parser for JSON files"""

    @staticmethod
    def parse(file: Path | bytes, encoding: str = None, as_text: bool = True, **kwargs) -> dict:
        """Parse a JSON file"""
        if isinstance(file, (str, Path)):
            with open(Path(file), "rb", encoding=encoding) as fb:
                data = json.load(fb)
        elif isinstance(file, bytes):
            data = json.load(file)
        else:
            raise TypeError(f"Cannot parse JSON for {type(file)}")

        return {"text": {"source": data}} if as_text is True else {"data": data}

    @staticmethod
    def stream(file_path: Path, buffer_size: int = 64 * 1024, **kwargs) -> dict:
        """Stream a JSON file"""
        with open(file_path, "rb") as fb:
            leading_character = get_leading_character(fb)
            prefix = "item" if leading_character == "[" else ""
            for item in ijson.items(fb, prefix=prefix, buf_size=buffer_size, use_float=True):
                yield item
