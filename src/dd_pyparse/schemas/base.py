from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import (BaseModel, ConfigDict, Field, FieldValidationInfo,
                      constr, field_validator)

from dd_pyparse.schemas.annotations.base import Annotation
from dd_pyparse.schemas.enums import DataType, Iso639_3
from dd_pyparse.schemas.fragments import Hash, Reference, Text


class Base(BaseModel):
    """Generic data object"""

    additional: Optional[dict[str, Any]] = Field(None, description="Additional metadata about the data")
    annotations: Optional[list[Annotation]] = Field(None, description="Annotations about the data")
    dataset: Optional[constr(to_upper=True, strip_whitespace=True, strict=True)] = Field(None, description="Dataset name")
    data_type: Optional[DataType] = Field(None, example=DataType.image, description="Data type")
    date_ingested: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(), description="Date and time the data was ingested into the system"
    )
    hash: Optional[Hash] = Field(None, description="Hashes of the file or meaningful data")
    id: str = Field(default_factory=lambda: uuid4().hex, description="Unique ID")
    languages: Optional[list[Iso639_3]] = Field(None, description="Languages used in the data")
    parent_id: Optional[str] = Field(None, description="Parent ID")
    references: Optional[list[Reference]] = Field(None, description="References to other data")
    summary: Optional[str] = Field(None, description="Summary of the data")
    text: Optional[Text] = Field(None, description="Text data")
    children: Optional[list[Any]] = Field(None, description="Children of the data")
    model_config: ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)

    @field_validator("children")
    def link_children(cls, children, info: FieldValidationInfo):
        if children:
            for child in children:
                child.parent_id = info.data["id"]
                child.dataset = info.data["dataset"]
        return children

# Base.model_rebuild(raise_errors=False)