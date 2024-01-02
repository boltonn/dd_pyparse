from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import Field

from dd_pyparse.schemas.base import Base
from dd_pyparse.schemas.enums import FileType


class File(Base):
    absolute_path: Optional[Path] = Field(None, description="URL of the file for retrieval")
    date_created: Optional[datetime] = Field(None, description="Date and time the data was created on source")
    date_modified: Optional[datetime] = Field(None, description="Date and time the data was modified on source")
    file_ext: Optional[str] = Field(None, example="jpg", description="File extension of the data")
    file_name: Optional[str] = Field(None, description="Filename of the file at source")
    file_size: Optional[int] = Field(None, example=10000, description="Size in bytes of the data")
    file_type: Optional[FileType] = Field(None, description="Type of file")
    file_uri: Optional[str] = Field(None, description="URI of the file at source")
    mime_type: Optional[str] = Field(None, example="image/jpeg", description="MIME type of the data")
