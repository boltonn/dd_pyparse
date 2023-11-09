from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import field_validator, BaseModel, Field

from pyparse.schemas.annotations.base import Annotation
from pyparse.schemas.enums import DataType
from pyparse.schemas.fragments import Reference


class RogueBase(BaseModel):
    """Generic data object"""

    id: Optional[str] = Field(None, description="UUID of the object", alias="_id")
    data_type: DataType = Field(..., example=DataType.image, description="Rogue base data type")
    parent_id: Optional[str] = Field(None, description="UUID of the parent object")
    date_uploaded: Optional[datetime] = Field(None, description="Date and time the data was uploaded to the system")
    annotations: Optional[list[Annotation]] = Field(None, description="Size in bytes of the data")
    references: Optional[list[Reference]] = Field(None, description="References to other data")
    additional: Optional[dict[str, Any]] = Field(None, description="Additional metadata about the data")

    @field_validator("id")
    @classmethod
    def set_id(cls, _id):
        return str(uuid4()) if _id is None else _id

    @field_validator("date_uploaded")
    @classmethod
    def set_date_uploaded(cls, date_uploaded):
        return datetime.now() if date_uploaded is None else date_uploaded