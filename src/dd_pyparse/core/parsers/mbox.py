from mailbox import mbox
from pathlib import Path
from typing import Iterator

from loguru import logger

from dd_pyparse.core.parsers.base import FileStreamer
from dd_pyparse.core.parsers.email import EmailParser
from dd_pyparse.schemas.data.email import Email


class MboxParser(FileStreamer):
    """Parser for mbox files"""

    @staticmethod
    def stream(
        file_path: Path, return_raw_header: bool = True, extract_children: bool = False, out_dir: Path = None, **kwargs
    ) -> Iterator[Email]:
        """Stream an mbox file"""
        msg_generator = mbox(file_path)
        logger.info(f"Found {len(msg_generator)} messages in {file_path}")
        for i, msg in enumerate(msg_generator):
            try:
                out = {
                    **EmailParser.parse_meta(msg=msg, return_raw_header=return_raw_header),
                    **EmailParser.parse_parts(msg=msg, extract_children=extract_children, out_dir=out_dir),
                }
                yield Email(**out)
            except Exception as e:
                logger.error(f"Error parsing message {i}: {e}")
                continue
