from typing import Literal, Optional

from pydantic import Field, field_validator

from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.data.parents.message import Message
from dd_pyparse.schemas.enums import DataType


class Email(File, Message):
    data_type: Literal["email"] = Field(DataType.email)
    subject: Optional[str] = Field(None, description="Email subject")
    header: Optional[dict[str, str]] = Field(None, description="Email header to include raw from, to, cc, bcc")
    is_archived: Optional[bool] = Field(None, description="Whether the email is archived")
    is_auto_forwarded: Optional[bool] = Field(None, description="Whether the email is auto forwarded")
    is_encrypted: Optional[bool] = Field(None, description="Whether the email is encrypted")
    is_flagged: Optional[bool] = Field(None, description="Whether the email is flagged or starred")
    is_forwarded: Optional[bool] = Field(None, description="Whether the email is forwarded")
    is_read: Optional[bool] = Field(None, description="Whether the email is read")
    is_signed: Optional[bool] = Field(None, description="Whether the email has a digital signature")
    is_spam: Optional[bool] = Field(None, description="Whether the email is flagged as spam")

    @field_validator("header")
    def remove_empty_header_fields(cls, v):
        return {k.lower(): v for k, v in v.items() if v is not None and v != ""}
