import email
from datetime import datetime
from email.header import decode_header, make_header
from email.message import Message
from pathlib import Path
import re

from loguru import logger

from pyparse.parsers.file import FileParser


class EmailParser:
    @staticmethod
    def load_bytes(raw: bytes):
        return email.message_from_bytes(raw)

    @staticmethod
    def load_filesystem(filepath: Path):
        with open(filepath, "rb") as fp:
            return email.message_from_binary_file(fp)

    @staticmethod
    def parse_date(date_str: str):
        date_tup = email.utils.parsedate_tz(date_str)
        date_time = datetime.fromtimestamp(email.utils.mktime_tz(date_tup))
        date_time = date_time.isoformat()
        return date_time

    @staticmethod
    def parse_headers(msg: Message, return_raw: bool = False):
        out = {}
        sender = None
        receivers = set()
        header = dict(msg).copy()

        for key in ["From", "To", "Cc", "Bcc"]:
            if key in header:
                emails = [re.sub('\s+', '', address) for _, address in email.utils.getaddresses(msg.get_all(key, []))]

                if key == "From":
                    # make the assumption we're only interested in the first argument which is From and not Sender
                    # see RFC documentation for more detail
                    sender = emails[0]
                else:
                    receivers.update(set(emails))

                out[key.lower()] = str(make_header(decode_header(header[key])))
        out["sender"] = sender
        out["receivers"] = list(receivers)

        date_str = header.get("Date")
        if date_str:
            out["date_sent"] = EmailParser.parse_date(date_str)

        conversation_id = header.get("Message-ID")
        if conversation_id:
            out["conversation_id"] = conversation_id

        subject = header.get("Subject")
        if subject:
            out["subject"] = subject

        # delete fields that have been processed or changed to fit schema name
        if return_raw is False:
            for key in ["From", "To", "Cc", "Bcc", "Message-ID", "Date", "Subject"]:
                if key in header:
                    _ = header.pop(key)
        out["header"] = {str(k): str(v) for k,v in header.items()}

        return out

    @staticmethod
    def parse_body(msg: Message, delimiter: str = " "):
        body = []
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body.append(part.get_payload(decode=True).decode("utf-8"))
            elif content_type == "text/html":
                logger.warning("HTML content not supported")
            elif content_type.startswith("multipart/"):
                continue
            else:
                logger.error(f"Unknown content type: {content_type}")
        return delimiter.join(body).strip()

    @staticmethod
    def parse(email: bytes | Path):
        msg = EmailParser.load_bytes if isinstance(email, bytes) else EmailParser.load_filesystem(email)

        return {
            **FileParser.parse(email),
            **EmailParser.parse_headers(msg), 
            "text": EmailParser.parse_body(msg)
        }
