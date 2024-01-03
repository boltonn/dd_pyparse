import email
import re
from dataclasses import dataclass
from datetime import datetime
from email.header import decode_header, make_header
from email.message import Message
from pathlib import Path
from typing import Optional

import chardet
from iso639 import Language, LanguageNotFoundError
from loguru import logger

from dd_pyparse.core.parsers.base import FileParser, get_file_meta
from dd_pyparse.core.parsers.html import HtmlParser
from dd_pyparse.core.utils.general import get_encoding_families, map_unsupported_encoding, safe_open
from dd_pyparse.core.utils.text import clean, clean_extra_whitespace
from dd_pyparse.schemas.data.parents.file import File


@dataclass
class EmailAddress:
    name: Optional[str]
    address: str


class EmailParser(FileParser):
    @staticmethod
    def load_bytes(raw: bytes):
        return email.message_from_bytes(raw)

    @staticmethod
    def load_filesystem(file_path: Path, encoding: str = "ISO-8859-1"):
        with open(file_path, encoding=encoding) as fb:
            return email.message_from_file(fb)

    @staticmethod
    def clean_mime_header(header: str) -> list[str]:
        """Clean a MIME header"""
        return [clean_extra_whitespace(header_part) for header_part in header.split(";")]

    @staticmethod
    def decode_content(part: Message, encoding: str = "utf-8"):
        content = part.get_payload(decode=True)
        charset = part.get_content_charset(encoding)
        try:
            return content.decode(charset, errors="ignore")
        except LookupError:
            detected_encoding = chardet.detect(content).get("encoding")
            if detected_encoding:
                logger.debug(f"Using ddetected encoding {detected_encoding=}")
                return content.decode(detected_encoding, errors="ignore")
            else:
                logger.warning("Unable to detect encoding so falling back to ignore errors w/ utf-8")
                return content.decode(encoding, errors="ignore")
        except AttributeError:
            logger.warning("Unable to decode content")
            return content

    @staticmethod
    def get_mail_addresses(msg: Message, field: str):
        headers = msg.get_all(field, [])
        addresses = email.utils.getaddresses(headers)
        for i, (name, addr) in enumerate(addresses):
            try:
                name = decode_header(name)
            except UnicodeDecodeError:
                logger.warning(f"Unable to decode mail header {name}")
                name = None
            addresses[i] = EmailAddress(**{"name": name, "address": re.sub(r"\s+", "", addr)})
        return addresses

    @staticmethod
    def override_make_header(decoded_header: list[tuple[bytes, str]], errors=None) -> str:
        """
        Override make_header to ignore errors
        """
        if errors == "ignore":
            return "".join([x.decode(enc, errors=errors) if enc is not None else x.decode() for x, enc in decoded_header])
        elif errors == "strict":
            return make_header(decoded_header, errors=errors)
        else:
            temp = []
            for x, enc in decoded_header:
                if enc is not None:
                    valid_decode = None
                    try:
                        # try to decode with the specified encoding in email header
                        valid_decode = temp.append(x.decode(enc) if enc is not None else x.decode())
                        temp.append(valid_decode)
                    except LookupError:
                        enc = map_unsupported_encoding(enc)
                        valid_decode = temp.append(x.decode(enc) if enc is not None else x.decode())
                        temp.append(valid_decode)
                    except UnicodeDecodeError:
                        # try to detect encoding
                        guess_encoding = chardet.detect(x)["encoding"]
                        if guess_encoding is not None:
                            try:
                                valid_decode = x.decode(guess_encoding)
                                break
                            except UnicodeDecodeError:
                                logger.debug(f"chardet guessed {guess_encoding} for {x} but did not work") 
                                                           
                        # brute force with related encodings
                        potential_encodings = get_encoding_families(enc)
                        if potential_encodings:
                            for encoding in potential_encodings:
                                try:
                                    valid_decode = x.decode(encoding)
                                    logger.debug(f"Brute force decode with {encoding=} worked: {valid_decode=}")
                                    break
                                except UnicodeDecodeError:
                                    continue
                        if valid_decode is None:
                            partial_decode = x.decode(enc, errors="ignore")
                            logger.warning(f"Unable to decode header {x} with {enc=}. Ignoring errors gave: {partial_decode=}")
                            temp.append(partial_decode)
                        else:
                            temp.append(valid_decode)
            return "".join([x for x in temp if x is not None])

    @staticmethod
    def parse_date(date_str: str):
        date_tup = email.utils.parsedate_tz(date_str)
        date_time = datetime.fromtimestamp(email.utils.mktime_tz(date_tup))
        date_time = date_time.isoformat()
        return date_time

    @staticmethod
    def parse_mime_header_meta(clean_header: list[str]) -> dict:
        """Parse the meta data from a MIME header"""
        meta = {}
        for header_part in clean_header:
            if "=" in header_part:
                key, value = header_part.split("=", maxsplit=1)
                key = clean_extra_whitespace(key.replace('"', ""))
                value = clean_extra_whitespace(value.replace('"', ""))
                meta[key] = str(make_header(decode_header(value)))
        return meta

    @staticmethod
    def get_part_filename(part: Message) -> str:
        """Get the filename of a MIME part"""
        file_name = part.get_filename()
        if file_name:
            temp = decode_header(file_name)
            logger.debug(f"{temp=}")
            if temp[0][1] is not None:
                return temp[0][0].decode(temp[0][1])

    @staticmethod
    def get_filename_from_content_type(content_type: str) -> str:
        """Get the filename from a MIME content type. Seems applicable in gmail"""
        content_type = EmailParser.clean_mime_header(content_type)
        meta = EmailParser.parse_mime_header_meta(content_type)
        return meta.get("name")

    @staticmethod
    def parse_attachment(
        part: Message, content_disposition: str, content_type: str, extract_children: bool = False, out_dir: Path = None
    ) -> dict:
        """Parse an attachment"""
        meta = EmailParser.parse_mime_header_meta(content_disposition)
        payload = part.get_payload(decode=True)
        
        if payload is None:
            logger.warning(f"Empty payload for {meta=}")
            return None
        
        meta |= get_file_meta(payload)

        # a series of ways to find the filename
        file_name = meta.get("filename")
        file_name = file_name if file_name else EmailParser.get_part_filename(part)
        file_name = (
            EmailParser.get_filename_from_content_type(content_type=content_type)
            if file_name is None and content_type is not None
            else file_name
        )
        if file_name is None:
            md5 = meta["hash"]["md5"]
            logger.warning(f"Unable to get filename for attachment w/ {md5=}")
        else:
            if "." in file_name:
                meta["file_extension"] = f".{file_name.split('.')[-1]}"
            meta["file_name"] = file_name
        meta["file_size"] = len(payload)

        date_modified = meta.pop("modification-date", None)
        if date_modified:
            meta["date_modified"] = EmailParser.parse_date(date_modified)

        date_created = meta.pop("creation-date", None)
        if date_created:
            meta["date_created"] = EmailParser.parse_date(date_created)

        if extract_children:
            out_file_ext = meta.get("file_extension", ".bin") or ".bin"
            out_file_name = meta["hash"]["md5"] + out_file_ext
            out_path = out_dir / out_file_name
            with safe_open(out_path, "wb") as fb:
                fb.write(payload)
            meta["absolute_path"] = str(out_path)
            logger.info(f"Extracted attachment to {out_path}")
        return File(**meta)

    @staticmethod
    def parse_header(header: dict):
        """Parse the header of an email"""
        out = {}
        for key, value in header.items():
            decoded_header = decode_header(value)
            try:
                out[key] = str(make_header(decoded_header))
            except (UnicodeDecodeError, LookupError):
                out[key] = EmailParser.override_make_header(decoded_header)
        return out

    @staticmethod
    def parse_meta(msg: Message, return_raw_header: bool = False) -> dict:
        """Parse and standardize the meta data of an email"""
        out = {}
        header = dict(msg.items()).copy()
        header = EmailParser.parse_header(header)
        header = {key.lower(): value for key, value in header.items()}

        subject = header.pop("subject", None)
        if subject is not None:
            out["subject"] = subject.strip()

        recipients = set()
        for key in ["from", "to", "cc", "bcc"]:
            addresses = [e.address for e in EmailParser.get_mail_addresses(msg, key)]

            if key == "from" and addresses:
                # per RFC 2822, the "From" field is a single address but someone can send on behalf of someone else
                out["sender"] = addresses[0]
            else:
                recipients.update(set(addresses))
        if recipients:
            out["recipients"] = list(recipients)

        date_sent = header.pop("date", None)
        if date_sent is not None:
            out["date_sent"] = EmailParser.parse_date(date_sent)

        out["conversation_id"] = header.pop("thread-index", None)

        language = header.pop("Content-Language", None)
        if language is not None and isinstance(language, str):
            language = language.split("-")[0].lower() if "-" in language else language.lower()
            try:
                # iso639-3
                out["languages"] = [Language.match(language).part3]
            except LanguageNotFoundError:
                logger.warning(f"Unable to parse language {language}")

        if return_raw_header:
            out["header"] = header

        return out

    @staticmethod
    def parse_parts(
        msg: Message,
        cleaned: bool = False,
        delimiter: str = "\n\n",
        extract_children: bool = False,
        out_dir: Path = None,
    ) -> dict:
        """Parse the MIME parts of an email"""

        html_content = []
        plain_content = []
        attachments = []

        # Note: this is a recursive function
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition", None)
            if content_disposition is not None:
                content_disposition = EmailParser.clean_mime_header(content_disposition)

                if content_type.startswith("multipart"):
                    continue

                elif "attachment" in content_disposition:
                    meta = EmailParser.parse_attachment(
                        part=part,
                        content_disposition=content_disposition,
                        content_type=content_type,
                        extract_children=extract_children,
                        out_dir=out_dir,
                    )
                    if meta:
                        attachments.append(meta)

            elif content_type == "text/plain":
                try:
                    plain_content.append(EmailParser.decode_content(part))
                except AttributeError as err:
                    logger.warning(f"Unable to decode text content: {err}")

            elif content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    html_content.append(HtmlParser.parse_str(payload))

        plain_content = delimiter.join(plain_content)
        html_content = delimiter.join(html_content)

        text = html_content + plain_content
        out = {}
        if text:
            if cleaned:
                text = clean(text)
            out["text"] = {"source": text}
        if attachments:
            out["attachments"] = attachments

        return out

    @staticmethod
    def parse(
        file: bytes | Path,
        encoding: str = None,
        return_raw_header: bool = False,
        extract_children: bool = False,
        out_dir: Path = None,
    ):
        """Parse an email"""
        if isinstance(file, bytes):
            msg = EmailParser.load_bytes(file)
        elif isinstance(file, (str, Path)):
            msg = EmailParser.load_filesystem(file_path=Path(file), encoding=encoding)
        else:
            raise TypeError(f"Cannot parse {type(file)}")

        return {
            **EmailParser.parse_meta(msg=msg, return_raw_header=return_raw_header),
            **EmailParser.parse_parts(msg=msg, extract_children=extract_children, out_dir=out_dir),
        }
