from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import Field

from pyparse.schemas.enums import Hash
from pyparse.schemas.base import RogueBase


class File(RogueBase):
    url: Optional[str] = Field(None, description="URL of the file for retrieval by Rogue")
    file_path: Optional[Path] = Field(None, description="Filepath of the file at source")
    file_name: Optional[str] = Field(None, description="Filename of the file at source")
    file_ext: Optional[str] = Field(None, example="jpg", description="File extension of the data")
    hashes: Optional[dict[Hash, str]] = Field(None, description="Hashes of the file")
    mime_type: Optional[str] = Field(None, example="image/jpeg", description="MIME type of the data")
    file_size: Optional[int] = Field(None, example=10000, description="Size in bytes of the data")
    date_created: Optional[datetime] = Field(None, description="Date and time the data was created on source")
    date_modified: Optional[datetime] = Field(None, description="Date and time the data was modified on source")