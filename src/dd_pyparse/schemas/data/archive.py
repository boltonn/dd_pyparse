from typing import Literal, Optional

from pydantic import Field

from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import DataType


class Archive(File):
    data_type: Literal["archive"] = Field(DataType.archive)
    num_children: Optional[int] = Field(None, description="Number of children contained in the archive")
