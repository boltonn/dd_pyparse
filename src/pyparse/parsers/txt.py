from hashlib import md5, sha1, sha256
from pathlib import Path

import magic

from pyparse.parsers.file import FileParser
from pyparse.schemas.data.document import Document


class TxtParser(FileParser):

    @staticmethod
    def parse_text(file_path: Path, encoding:str = None) -> str:
        with open(file_path, "r", encoding=encoding) as fb:
            txt = fb.read()
        return txt


    @staticmethod
    def parse(file: Path | bytes, encoding=None) -> Document:
        meta = FileParser.parse(file=file, encoding=encoding)
        meta['text'] = file.decode(encoding) if isinstance(file, bytes) else TxtParser.parse_text(file)
        return meta
