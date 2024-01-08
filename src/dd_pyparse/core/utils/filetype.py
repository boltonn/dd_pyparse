import mimetypes
from typing import IO, Optional

import magic
from loguru import logger

from dd_pyparse.core.utils.general import get_n_from_file
from dd_pyparse.core.utils.patterns import EMAIL_HEADER_RE
from dd_pyparse.schemas.enums import FileType


# map of mime types to file types and most common extension
MIME_TYPE_MAP: dict[str, (FileType, str)] = {
    "application/csv": (FileType.csv, ".csv"),
    "application/gzip": (FileType.gzip, ".gz"),
    "application/javascript": (FileType.code, ".js"),
    "application/json": (FileType.json, ".json"),
    "application/mbox": (FileType.mbox, ".mbox"),
    "application/msword": (FileType.doc, ".doc"),
    "application/pdf": (FileType.pdf, ".pdf"),
    "application/sql": (FileType.code, ".sql"),
    "application/tar+gzip": (FileType.tar, ".tar.gz"),
    "application/vnd.apple.keynote": (FileType.ppt, ".key"),
    "application/vnd.ms-excel": (FileType.xls, ".xls"),
    "application/vnd.ms-outlook": (FileType.msg, ".msg"),
    "application/vnd.ms-powerpoint": (FileType.ppt, ".ppt"),
    "application/vnd.ms-word.document.macroEnabled.main+xml": (FileType.doc, ".docm"),
    "application/vnd.ms-word.template.macroEnabledTemplate.main+xml": (FileType.doc, ".dotm"),
    "application/vnd.oasis.opendocument.presentation": (FileType.ppt, ".odp"),
    "application/vnd.oasis.opendocument.spreadsheet": (FileType.ods, ".ods"),
    "application/vnd.oasis.opendocument.text": (FileType.doc, ".odt"),
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": (FileType.xlsx, ".xlsx"),
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": (FileType.pptx, ".pptx"),
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow": (FileType.ppt, ".pps"),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (FileType.docx, ".docx"),
    "application/x-7z-compressed": (FileType.zip, ".zip"),
    "application/x-bzip2": (FileType.bz2, ".bz2"),
    "application/x-csv": (FileType.csv, ".csv"),
    "application/x-gzip": (FileType.gzip, ".gz"),
    "application/x-httpd-php": (FileType.code, ".php"),
    "application/x-ole-storage": (FileType.msg, ".msg"),
    "application/x-rar-compressed": (FileType.rar, ".rar"),
    "application/x-tar": (FileType.tar, ".tar"),
    "application/xml": (FileType.xml, ".xml"),
    "application/zip": (FileType.zip, ".zip"),
    # "audio/mpeg": (FileType.mp3, ".mp3"),
    # "audio/x-wav": (FileType.wav, ".wav"),
    "image/avif": (FileType.image, ".avif"),
    "image/avif-sequence": (FileType.image, ".avifs"),
    "image/bmp": (FileType.image, ".bmp"),
    "image/gif": (FileType.image, ".gif"),
    "image/heic": (FileType.image, ".heic"),
    "image/heic-sequence": (FileType.image, ".heics"),
    "image/heif": (FileType.image, ".heif"),
    "image/heif-sequence": (FileType.image, ".heifs"),
    "image/jpeg": (FileType.image, ".jpg"),
    "image/jpg": (FileType.image, ".jpg"),
    "image/jp2": (FileType.image, ".jp2"),
    "image/png": (FileType.image, ".png"),
    "image/tiff": (FileType.image, ".tiff"),
    "image/webp": (FileType.image, ".webp"),
    "image/wmf": (FileType.image, ".wmf"),
    "image/x-icon": (FileType.image, ".ico"),
    "image/x-jb2": (FileType.image, ".jb2"),
    "image/x-jbig2": (FileType.image, ".jbig2"),
    "message/rfc822": (FileType.eml, ".eml"),
    # "text/calendar": (FileType.ics, ".ics"),
    "text/csv": (FileType.csv, ".csv"),
    "text/comma-separated-values": (FileType.csv, ".csv"),
    "text/html": (FileType.html, ".html"),
    "text/markdown": (FileType.txt, ".md"),
    "text/plain": (FileType.txt, ".txt"),
    "text/richtext": (FileType.doc, ".rtf"),
    "text/tab-separated-values": (FileType.tsv, ".tsv"),
    "text/xml": (FileType.xml, ".xml"),
    "text/x-7z-compressed": (FileType.zip, ".zip"),
    "text/x-bzip2": (FileType.bz2, ".bz2"),
    "text/x-c": (FileType.code, ".c"),
    "text/x-c++": (FileType.code, ".cpp"),
    "text/x-c++src": (FileType.code, ".cpp"),
    "text/x-clojure": (FileType.code, ".clj"),
    "text/x-coffeescript": (FileType.code, ".coffee"),
    "text/x-common-lisp": (FileType.code, ".lisp"),
    "text/x-comma-separated-values": (FileType.csv, ".csv"),
    "text/x-csharp": (FileType.code, ".cs"),
    "text/x-csrc": (FileType.code, ".c"),
    "text/x-csv": (FileType.csv, ".csv"),
    "text/x-dart": (FileType.code, ".dart"),
    "text/x-erlang": (FileType.code, ".erl"),
    "text/x-fortran": (FileType.code, ".f"),
    "text/x-go": (FileType.code, ".go"),
    "text/x-haskell": (FileType.code, ".hs"),
    "text/x-haxe": (FileType.code, ".hx"),
    "text/x-java": (FileType.code, ".java"),
    "text/x-javascript": (FileType.code, ".js"),
    "text/x-julia": (FileType.code, ".jl"),
    "text/x-kotlin": (FileType.code, ".kt"),
    "text/x-latex": (FileType.code, ".tex"),
    "text/x-lisp": (FileType.code, ".lisp"),
    "text/x-lua": (FileType.code, ".lua"),
    "text/x-markdown": (FileType.code, ".md"),
    "text/x-matlab": (FileType.code, ".m"),
    "text/x-msdos-batch": (FileType.code, ".bat"),
    "text/x-nim": (FileType.code, ".nim"),
    "text/x-objectivec": (FileType.code, ".m"),
    "text/x-ocaml": (FileType.code, ".ml"),
    "text/x-pascal": (FileType.code, ".pas"),
    "text/x-perl": (FileType.code, ".pl"),
    "text/x-php": (FileType.code, ".php"),
    "text/x-powershell": (FileType.code, ".ps1"),
    "text/x-prolog": (FileType.code, ".pro"),
    "text/x-python": (FileType.code, ".py"),
    "text/x-rar": (FileType.rar, ".rar"),
    "text/x-r": (FileType.code, ".r"),
    "text/x-ruby": (FileType.code, ".rb"),
    "text/x-rst": (FileType.txt, ".rst"),
    "text/x-rustsrc": (FileType.code, ".rs"),
    "text/x-scala": (FileType.code, ".scala"),
    "text/x-scheme": (FileType.code, ".scm"),
    "text/x-shellscript": (FileType.code, ".sh"),
    "text/x-sql": (FileType.code, ".sql"),
    "text/x-swift": (FileType.code, ".swift"),
    "text/x-tar": (FileType.tar, ".tar"),
    "text/x-typescript": (FileType.code, ".ts"),
    "text/x-vbnet": (FileType.code, ".vb"),
    # "text/x-vcard": (FileType.vcf, ".vcf"),
    "text/x-yaml": (FileType.txt, ".yaml"),
    "text/x-zip": (FileType.zip, ".zip"),
}

# supplementing extension map if there is more than one extension for a file type
ADDITIONAL_EXTENSIONS = {
    ".jpf": (FileType.image, "image/x-jpf"),
    ".java": (FileType.txt, "text/plain"),
    ".kth": (FileType.ppt, "application/vnd.apple.keynote"),
    ".log": (FileType.log, "text/plain"),
    ".pot": (FileType.ppt, "application/vnd.ms-powerpoint"),
    ".pps": (FileType.ppt, "application/vnd.ms-powerpoint"),
    ".tab": (FileType.tsv, "text/tab-separated-values"),
    ".vb": (FileType.txt, "text/plain"),
}
EXT_TO_FILETYPE_MIME_MAP = {ext: (ftyp, mtype) for mtype, (ftyp, ext) in MIME_TYPE_MAP.items()} | ADDITIONAL_EXTENSIONS


def get_extension(file_name: str) -> str:
    file_ext = "." + file_name.split(".")[-1] if "." in file_name else None
    if file_ext:
        return ".tar.gz" if file_ext.endswith(".tar.gz") else file_ext.lower()


def guess_extension(mime_type: str) -> str:
    """Guess the extension of a file based on its mime type"""
    _, ext = MIME_TYPE_MAP.get(mime_type, (None, None))
    return mimetypes.guess_extension(mime_type) if ext is None else ext


def is_mbox(file: IO) -> bool:
    """Check if a file is an mbox file"""
    return get_n_from_file(file, 5) == b"From "


def is_text_json(file: IO) -> bool:
    """Check if a file of filetype text/plain is json"""
    first_char = get_n_from_file(file, 1)
    try:
        last_char = get_n_from_file(file, -1)
    except OSError:
        return False

    return first_char == b"{" and last_char == b"}" or first_char == b"[" and last_char == b"]"


def is_buffer_email(file: IO) -> bool:
    """Check if a file is an email based off header common in .eml"""
    file_content = get_n_from_file(file, 4096)
    file_header = file_content.decode(errors="ignore") if isinstance(file_content, bytes) else file_content
    return EMAIL_HEADER_RE.match(file_header) is not None


def mimetype_magic_plus(file: IO) -> None | str:
    """A set of custom magic numbers plus magic as a fallback"""
    # Note: pick the longest known magic number size
    file_content = get_n_from_file(file, 35)
    heif_span = file_content[8:12]
    mime_type = None
    if file_content[:2] == b"BM":
        mime_type = "image/bmp"
    elif file_content[:4] == b"\x89PNG":
        mime_type = "image/png"
    elif file_content[:2] == b"\xff\xd8":
        mime_type = "image/jpeg"
    elif heif_span == b"avif":
        mime_type = "image/avif"
    elif heif_span == b"avis":
        mime_type = "image/avif-sequence"
    elif heif_span in [b"heic", b"heix", b"heim", "heis"]:
        mime_type = "image/heic"
    elif heif_span in [b"hevc", b"hevx", b"hevm", "hevs"]:
        mime_type = "image/heic-sequence"
    elif heif_span == b"mif1":
        mime_type = "image/heif"
    elif heif_span == b"msf1":
        mime_type = "image/heif-sequence"
    else:
        mime_type = magic.from_buffer(get_n_from_file(file, 4096), mime=True)
    return mime_type


def route_mime_type(
    file_name: Optional[str] = None,
    file: Optional[IO] = None,
    mime_type: Optional[str] = None,
) -> tuple[str, FileType]:
    """Route the mime type of a file to a file type"""

    file_ext = get_extension(file_name) if file_name is not None else None

    # Use the magic numbers first and foremost
    # Note: dont always trust the user to know the mime_type or other software
    if file is not None:
        mime_type = mimetype_magic_plus(file)
        logger.debug(f"Magic or custom magic numbers identified mime type: {mime_type}")

    # Mime type is not always accurate, so we can use the file extension or file to help
    if mime_type is not None:
        if mime_type.endswith("/xml"):
            file_type = FileType.html if file_ext and (file_ext in [".html", ".htm"]) else FileType.xml

        elif mime_type == "text/plain":
            # magic overwrites for text files
            if is_mbox(file=file):
                file_type = FileType.mbox
                mime_type = "application/mbox"
            elif is_buffer_email(file=file):
                file_type = FileType.email
                mime_type = "message/rfc822"
            elif is_text_json(file=file):
                file_type = FileType.json
                mime_type = "application/json"
            elif file_ext and file_ext in EXT_TO_FILETYPE_MIME_MAP:
                file_type, mime_type = EXT_TO_FILETYPE_MIME_MAP[file_ext]
            else:
                file_type = FileType.txt

        else:
            file_type, _ = MIME_TYPE_MAP.get(mime_type, (None, None))
            # magic overwrites for documents and presentations
            if file_type == FileType.docx:
                if file_ext == ".docm":
                    file_type = FileType.doc
                    mime_type = "application/vnd.ms-word.document.macroEnabled.main+xml"
                elif file_ext == ".dotm":
                    file_type = FileType.doc
                    mime_type = "application/vnd.ms-word.template.macroEnabledTemplate.main+xml"
                elif file_ext == ".odt":
                    file_type = FileType.doc
                    mime_type = "application/vnd.oasis.opendocument.text"

            if file_type == FileType.pptx:
                if file_ext == ".pps":
                    file_type = FileType.ppt
                    mime_type = "application/vnd.openxmlformats-officedocument.presentationml.slideshow"
                elif file_ext == ".ppt":
                    file_type = FileType.ppt
                    mime_type = "application/vnd.ms-powerpoint"
                elif file_ext == ".odp":
                    file_type = FileType.ppt
                    mime_type = "application/vnd.oasis.opendocument.presentation"
                elif file_ext == ".pot":
                    file_type = FileType.ppt
                    mime_type = "application/vnd.ms-powerpoint"
                elif file_ext in [".key", ".kth"]:
                    file_type = FileType.ppt
                    mime_type = "application/vnd.apple.keynote"

    if file_type is None and file_ext is not None:
        logger.info(f"Using file extension {file_ext} to identify mime type")
        file_type, mime_type = EXT_TO_FILETYPE_MIME_MAP.get(file_ext, (file_type, mime_type))
        
    if file_type is None:
        file_type = FileType.unknown

    if file is not None:
        file.seek(0)
    return mime_type, file_type
