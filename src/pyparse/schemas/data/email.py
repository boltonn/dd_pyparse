from typing import Optional

from pydantic import Field

from pyparse.schemas.enums import DataType
from pyparse.schemas.data.parents.message import Message


class Email(Message):
    data_type = DataType.email
    from_address: str = Field(..., description="Sender email address", alias="from")
    to: Optional[str] = Field(None, description="Recipient(s) email addresses")
    cc: Optional[str] = Field(None, description="CC recipient(s) email addresses")
    bcc: Optional[str] = Field(None, description="BCC recipient(s) email addresses")
    subject: Optional[str] = Field(None, description="Email subject")
    text: Optional[str] = Field(
        None,
        description="Email body text (not including attachements); HTML should be parsed",
    )
    header: Optional[dict[str, str]] = Field(None, description="Email header")
    has_attachments: Optional[bool] = Field(None, description="Whether the email has attachments")
