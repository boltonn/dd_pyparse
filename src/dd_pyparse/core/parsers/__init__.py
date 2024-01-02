from pathlib import Path
from typing import Literal

from dd_pyparse.core.parsers.base import (FileParser, FileStreamer,
                                          get_file_meta)
from dd_pyparse.core.parsers.csv import CsvParser
from dd_pyparse.core.parsers.doc import DocParser
from dd_pyparse.core.parsers.docx import DocxParser
from dd_pyparse.core.parsers.email import EmailParser
from dd_pyparse.core.parsers.gzip import GzipParser
from dd_pyparse.core.parsers.html import HtmlParser
from dd_pyparse.core.parsers.image import ImageParser
from dd_pyparse.core.parsers.json import JsonParser
from dd_pyparse.core.parsers.mbox import MboxParser
from dd_pyparse.core.parsers.msg import MsgParser
from dd_pyparse.core.parsers.pdf import PdfParser
from dd_pyparse.core.parsers.pptx import PptxParser
from dd_pyparse.core.parsers.rar import RarParser
from dd_pyparse.core.parsers.sevenzip import SevenZipParser
from dd_pyparse.core.parsers.tar import TarParser
from dd_pyparse.core.parsers.tsv import TsvParser
from dd_pyparse.core.parsers.txt import TxtParser
from dd_pyparse.core.parsers.video import VideoParser
from dd_pyparse.core.parsers.xls import XlsParser
from dd_pyparse.core.parsers.xlsx import XlsxParser
from dd_pyparse.core.parsers.xml import XmlParser
from dd_pyparse.core.parsers.zip import ZipParser
from dd_pyparse.schemas.data import Archive, Document, Email, Image, Video
from dd_pyparse.schemas.enums import DataType, FileType
from dd_pyparse.utils.exceptions import UnsupportedFileType

PARSER_REGISTRY = {
    FileType.csv: (CsvParser, Document),
    FileType.doc: (DocParser, Document),
    FileType.docx: (DocxParser, Document),
    FileType.eml: (EmailParser, Email),
    FileType.gzip: (GzipParser, Archive),
    FileType.html: (HtmlParser, Document),
    FileType.image: (ImageParser, Image),
    FileType.json: (JsonParser, Document),
    FileType.mbox: (MboxParser, Archive),
    FileType.msg: (MsgParser, Email),
    FileType.pdf: (PdfParser, Document),
    FileType.pptx: (PptxParser, Document),
    FileType.rar: (RarParser, Archive),
    FileType.sevenzip: (SevenZipParser, Archive),
    FileType.tar: (TarParser, Archive),
    FileType.tsv: (TsvParser, Document),
    FileType.txt: (TxtParser, Document),
    FileType.video: (VideoParser, Video),
    FileType.xls: (XlsParser, Document),
    FileType.xlsx: (XlsxParser, Document),
    FileType.xml: (XmlParser, Document),
    FileType.zip: (ZipParser, Archive),
}


def route_parser(file_type: FileType) -> tuple[FileParser | FileStreamer, DataType]:
    """Route a file type to a parser and pydantic validator"""
    try:
        parser, validator = PARSER_REGISTRY[file_type]
    except KeyError:
        raise UnsupportedFileType(f"Unsupported file type: {file_type=}")
    return parser, validator


def parse(file_path: Path, mode: Literal["dict", "json"] = "dict", extract_children: bool = False, out_dir: Path = None, **kwargs) -> dict:
    """Parse a file and return a dictionary of metadata"""
    out = get_file_meta(file_path)
    processor, validator = route_parser(file_type=out["file_type"])

    if issubclass(processor, FileParser):
        update = processor.parse(file=file_path, extract_children=extract_children, out_dir=out_dir, **kwargs)
        out = update | out

    elif issubclass(processor, FileStreamer):
        children = [child for child in processor.stream(file_path=file_path, extract_children=extract_children, out_dir=out_dir, **kwargs)]
        out["children"] = children if children else None

    out = validator(**out)
    return out.model_dump(mode=mode, exclude_none=True)
