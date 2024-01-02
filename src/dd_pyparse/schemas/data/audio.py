from typing import Literal, Optional

from pydantic import Field

from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import DataType


class Audio(File):
    data_type: Literal["audio"] = Field(DataType.audio)
    duration: Optional[float] = Field(None, description="Duration of the audio (ms)")
    num_samples: Optional[int] = Field(None, description="Number of samples in the audio")
    sample_rate: Optional[int] = Field(None, description="Sample rate of the audio")
    num_channels: Optional[int] = Field(None, description="Number of channels in the audio")
    bit_rate: Optional[int] = Field(None, description="Bit rate of the audio")
    bit_depth: Optional[int] = Field(None, description="Bit depth of the audio")
