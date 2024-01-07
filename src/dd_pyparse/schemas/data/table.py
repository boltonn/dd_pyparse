from typing import Literal, Optional

from pydantic import ConfigDict, Field

from dd_pyparse.schemas.base import Base
from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import DataType


class Table(File):
    """Generic table object"""

    data_type: Literal["table"] = Field(DataType.table)
    created_by: Optional[str] = Field(None, description="Author of the table")
    modified_by: Optional[str] = Field(None, description="Last user to modify the table")
    num_columns: Optional[int] = Field(None, description="Number of columns in the table")
    num_rows: Optional[int] = Field(None, description="Number of rows in the table")
    name: Optional[str] = Field(None, description="Name of the table")
    model_config = ConfigDict(use_enum_values=True)