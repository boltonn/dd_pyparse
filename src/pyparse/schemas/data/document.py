from typing import Optional

from pydantic import Field

from pyparse.schemas.enums import DataType
from pyparse.schemas.data.parents.file import File


class Document(File):
    data_type = DataType.document
    text: Optional[str] = Field(None, description="Text in the document (extracted or OCR'ed)")
    num_pages: Optional[int] = Field(None, example=2, description="Number of pages in the document")
    num_words: Optional[int] = Field(None, example=1000, description="Number of words in the document")
    num_characters: Optional[int] = Field(None, example=10000, description="Number of characters in the document")
    num_lines: Optional[int] = Field(None, example=20, description="Number of lines in the document")
