import warnings
from io import BytesIO
from pathlib import Path
import tempfile

from iso639 import Language, LanguageNotFoundError
from loguru import logger
from pandas import ExcelFile, read_excel

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.parsers.pdf import PdfParser
from dd_pyparse.core.utils.externals import convert_with_libre
from dd_pyparse.core.utils.text import clean

warnings.filterwarnings("ignore", category=UserWarning)

# TODO: max_pages parameter

MAPPINGS = {
    "creator": "created_by",
    "created": "date_created",
    "description": "summmary",
    "keywords": "keywords",
    "language": "language",
    "lastModifiedBy": "modified_by",
    "modified": "date_modified",
    "revision": "revision",
    "subject": "subject",
    "title": "title",
    "version": "version",
}


class XlsxParser(FileParser):
    @staticmethod
    def parse_meta(excel: ExcelFile, raw: bool = False, **kwargs) -> dict:
        """Parse the metadata from an xlsx file"""
        meta = excel.book.__dict__.get("properties", {})
        meta = {k: getattr(meta, k) for k in dir(meta) if not k.startswith("_")}
        meta = {k: (v.decode() if isinstance(v, bytes) else v) for k, v in meta.items() if v}
        language = meta.pop("language", None)
        if language:
            try:
                language = Language(language).part3
                meta["languages"] = [language]
            except LanguageNotFoundError:
                logger.warning(f"Failed to parse language {language}")
        return meta if raw is True else {k: v for k, v in meta.items() if v}

    @staticmethod
    def parse_text(
        excel: ExcelFile,
        cleaned: bool = True,
        paginated: bool = False,
        sheet_delimiter: str = "\n",
        **kwargs,
    ) -> str:
        """Parse the text from an xlsx file"""
        sheets = []
        for i, sheet_name in enumerate(excel.sheet_names):
            df = read_excel(excel, sheet_name=i)
            if df.empty is False:
                sheet_text = df.to_string(index=False, na_rep=" ")
                if cleaned:
                    sheet_text = clean(sheet_text, extra_whitespace=True, trailing_punctuation=True)
                sheets.append(f"Sheet {i}: {sheet_name}\n{sheet_text}")
        if paginated is False:
            return sheet_delimiter.join(sheets)
        return sheets

    @staticmethod
    def parse(
        file: Path | bytes,
        cleaned: bool = True,
        **kwargs,
    ) -> dict:
        """Parse an xlsx file"""
        if isinstance(file, bytes):
            file = BytesIO(file)
        elif isinstance(file, (Path, str)):
            file = Path(file)
        else:
            raise TypeError(f"Cannot parse {type(file)}")

        try:
            excel = ExcelFile(file)
            out = XlsxParser.parse_meta(excel=excel, raw=True)
            text = XlsxParser.parse_text(excel=excel, cleaned=cleaned)
            if text:
                out["text"] = {"source": text}
            return out
        except ValueError:
            logger.info(f"Pandas failed to parse {file.name} as xlsx. Falling back to pdf conversion and parsing")
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = convert_with_libre(
                    file_path=file,
                    tmp_dir=tmp_dir,
                    target_format="pdf",
                )

                return PdfParser.parse(
                    file=tmp_path,
                    cleaned=cleaned,
                    **kwargs,
                )