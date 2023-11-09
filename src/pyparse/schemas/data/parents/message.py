from datetime import datetime

from pydantic import Field

from pyparse.schemas.base import RogueBase


class Message(RogueBase):
    conversation_id: str = Field(..., description="Message ID")
    sender: str = Field(..., description="Sender")
    receivers: list[str] = Field(..., description="Receivers")
    date_sent: datetime = Field(..., description="Date and time message was sent")
