from typing import Any, Literal, Optional

from pydantic import Field, conint

from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import DataType


class Image(File):
    data_type: Literal["image"] = Field(DataType.image)
    width: Optional[conint(gt=0)] = Field(None, example=640, description="Width of the image")
    height: Optional[conint(gt=0)] = Field(None, example=640, description="Height of the image")
    exif: Optional[dict[str, Any]] = Field(
        None,
        example={
            "make": "Canon",
            "model": "Canon EOS 5D Mark III",
            "exposure_time": "1/60",
            "f_number": "f/10",
            "iso": "100",
        },
        description="Exif data of the image",
    )
