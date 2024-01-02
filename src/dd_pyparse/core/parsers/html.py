from pathlib import Path

from bs4 import BeautifulSoup

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.parsers.txt import TxtParser
from dd_pyparse.core.utils.text import clean


class HtmlParser(FileParser):
    """Parser for HTML files"""

    @staticmethod
    def parse_str(
        html_str: str,
        delimiter: str = "\n",
        exclude_tags: list[str] = ["script", "style"],
    ):
        """Parse a string of HTML"""
        soup = BeautifulSoup(html_str, "lxml")
        for tag in soup.find_all(exclude_tags):
            tag.decompose()
        return soup.get_text(separator=delimiter)

    @staticmethod
    def parse(
        file: Path | bytes,
        encoding: str = None,
        delimiter: str = "\n",
        raw: bool = False,
        exclude_tags: list[str] = ["script", "style"],
        cleaned: bool = True,
        **kwargs,
    ):
        """Parse an HTML file"""
        out = TxtParser.parse(file=file, encoding=encoding)
        text = out["text"]["source"]
        if text is not None:
            if raw is False:
                text = HtmlParser.parse_str(
                    html_str=out["text"]["source"],
                    delimiter=delimiter,
                    exclude_tags=exclude_tags,
                )
                if cleaned is True:
                    text = clean(text, extra_whitespace=True, trailing_punctuation=True)
            out["text"]["source"] = text
        return out
