from typing import Any, Optional

from pydantic import Field, conint

from pyparse.schemas.enums import DataType
from pyparse.schemas.data.parents.file import File



class Image(File):
    data_type = DataType.image
    text: Optional[str] = Field(None, description="OCR'ed text in the image")
    width: conint(gt=0) = Field(..., example=640, description="Width of the image")
    height: conint(gt=0) = Field(..., example=640, description="Height of the image")
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
