from io import BytesIO
from pathlib import Path

import pandas as pd
from loguru import logger
from pandas.errors import ParserError

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.parsers.txt import TxtParser


class CsvParser(FileParser):
    @staticmethod
    def parse(
        file: Path | bytes,
        delimiter: str = ",",
        encoding: str = None,
        **kwargs,
    ) -> dict:
        """Parse a csv file"""
        file = BytesIO(file) if isinstance(file, bytes) else file
        try:
            df = pd.read_csv(file, encoding=encoding, delimiter=delimiter)
            text = df.to_string(index=False, na_rep=" ")
            return {"text": {"source": text}}
        except ParserError:
            logger.warning(f"Failed to parse {file.name} as csv into table. Falling back to txt")
            return TxtParser.parse(file=file, encoding=encoding, **kwargs)