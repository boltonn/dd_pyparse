import codecs
from pathlib import Path

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.utils.text import clean


class TxtParser(FileParser):
    @staticmethod
    def parse(
        file: Path | bytes,
        encoding: str = None,
        cleaned: bool = True,
        **kwargs,
    ) -> dict:
        """Parse a txt file"""
        if isinstance(file, bytes):
            encoding = encoding or "utf-8"
            text = file.decode(encoding=encoding)
        elif isinstance(file, (Path, str)):
            with codecs.open(file, "r", encoding=encoding) as fb:
                text = fb.read()
        else:
            raise TypeError(f"Cannot parse {type(file)}")
        if cleaned:
            text = clean(text, extra_whitespace=True, trailing_punctuation=True)
        if text:
            return {"text": {"source": text}}
