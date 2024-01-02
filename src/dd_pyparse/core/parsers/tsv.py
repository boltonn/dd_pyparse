from pathlib import Path

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.parsers.csv import CsvParser


class TsvParser(FileParser):
    @staticmethod
    def parse(
        file: Path | bytes,
        encoding: str = None,
        delimiter: str = "\t",
        **kwargs,
    ) -> dict:
        """Parse a tsv file"""
        return CsvParser.parse(
            file=file,
            encoding=encoding,
            delimiter=delimiter,
            **kwargs,
        )
