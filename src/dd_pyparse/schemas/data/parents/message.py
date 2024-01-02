from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from dd_pyparse.schemas.base import Base
from dd_pyparse.schemas.enums import Direction, MessageState


class Message(Base):
    """Generic message object"""

    conversation_id: Optional[str] = Field(None, description="Conversation/Thread ID")
    date_sent: Optional[datetime] = Field(None, description="Date and time message was sent")
    direction: Optional[Direction] = Field(None, description="Direction of the message")
    message_id: Optional[str] = Field(None, description="Message ID")
    recipients: Optional[list[str]] = Field(None, description="Recipients")
    recipient_groups: Optional[list[str]] = Field(None, description="Recipient groups")
    reply_to_id: Optional[str] = Field(None, description="ID of the message this message is a reply to")
    sender: Optional[str] = Field(None, description="Sender")
    state: Optional[MessageState] = Field(None, description="State of the message")
    model_config = ConfigDict(use_enum_values=True)
