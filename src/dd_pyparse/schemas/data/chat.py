from typing import Literal

from pydantic import Field

from dd_pyparse.schemas.data.parents.message import Message
from dd_pyparse.schemas.enums import DataType


class ChatMessage(Message):
    data_type: Literal["chat_message"] = Field(DataType.chat_message)
