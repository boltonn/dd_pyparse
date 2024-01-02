from typing import Literal, Optional

from pydantic import Field

from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import DataType


class Document(File):
    data_type: Literal["document"] = Field(DataType.document)
    created_by: Optional[str] = Field(None, description="Author of the document")
    modified_by: Optional[str] = Field(None, description="Last user to modify the document")
    num_pages: Optional[int] = Field(None, example=2, description="Number of pages in the document")
    revision: Optional[int] = Field(None, description="Revision of the document")
    subject: Optional[str] = Field(None, description="Subject of the document")
    title: Optional[str] = Field(None, description="Title of the document")
    version: Optional[str] = Field(None, description="Version of the document")
