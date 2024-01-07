from typing import Literal, Optional

from pydantic import Field

from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import DataType


class Log(File):
    """Generic log object"""
    data_type: Literal["log"] = Field(DataType.log)
    format: Optional[str] = Field(None, description="Format of log")
    level: Optional[str] = Field(None, description="Level of log")
    retention: Optional[str] = Field(None, description="Retention of log")
    source: Optional[str] = Field(None, description="Source of log")
    type: Optional[str] = Field(None, description="Type of log")




