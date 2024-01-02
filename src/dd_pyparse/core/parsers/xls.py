from pathlib import Path

import olefile
from iso639 import Language, LanguageNotFoundError
from loguru import logger
from pandas import ExcelFile

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.parsers.xlsx import XlsxParser

MAPPINGS = {
    "author": "created_by",
    "create_time": "date_created",
    "description": "summmary",
    "keywords": "keywords",
    "language": "language",
    "last_saved_by": "modified_by",
    "last_saved_time": "date_modified",
    "revision_number": "revision",
    "subject": "subject",
    "title": "title",
    "doc_version": "version",
}


class XlsParser(FileParser):
    @staticmethod
    def parse_meta(file: Path | bytes, raw: bool = False, **kwargs) -> dict:
        """Parse the metadata from an xls file"""
        with olefile.OleFileIO(file) as ole:
            meta = ole.get_metadata()
            meta = {k: getattr(meta, k) for k in meta.SUMMARY_ATTRIBS + meta.DOCSUM_ATTRIBS}
            meta = {k: (v.decode() if isinstance(v, bytes) else v) for k, v in meta.items() if v}

            language = meta.pop("language", None)
            if language:
                try:
                    language = Language(language).part3
                    meta["languages"] = [language]
                except LanguageNotFoundError:
                    logger.warning(f"Failed to parse language {language}")

            return {MAPPINGS[k]: v for k, v in meta.items() if k in MAPPINGS and v} if raw is False else meta

    @staticmethod
    def parse(
        file: Path | bytes,
        encoding: str = None,
        **kwargs,
    ) -> dict:
        """Parse an xls file"""
        excel = ExcelFile(file)
        out = XlsParser.parse_meta(file=file, raw=True)
        text = XlsxParser.parse(excel=excel, encoding=encoding, **kwargs)
        if text:
            out["text"]["source"] = text
        return out
