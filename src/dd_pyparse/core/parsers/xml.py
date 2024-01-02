import xml.etree.ElementTree as ET
from pathlib import Path

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.parsers.txt import TxtParser
from dd_pyparse.core.utils.text import clean


class XmlParser(FileParser):
    @staticmethod
    def parse(
        file: Path | bytes,
        encoding: str = None,
        cleaned: bool = True,
        delimiter: str = "\n",
        raw: bool = False,
        xml_path: str = ".",
        **kwargs,
    ) -> dict:
        """Parse a xml file"""
        out = TxtParser.parse(
            file=file,
            encoding=encoding,
            cleaned=cleaned,
            delimiter=delimiter,
            **kwargs,
        )
        if raw is False and out.get("text"):
            raw_text = out.pop("text")
            raw_text = raw_text["source"]
            if raw_text:
                root = ET.fromstring(raw_text)
                leaf_elements = [
                    sub_el.text for el in root.findall(xml_path) for sub_el in el.iter() if hasattr(sub_el, "text") and sub_el.text
                ]
                text = delimiter.join(leaf_elements)
                if cleaned:
                    text = clean(text, extra_whitespace=True, trailing_punctuation=True)
                if text:
                    out["text"] = {"source": text}
        return out
