from enum import StrEnum

import iso639


class AddressType(StrEnum):
    home = "home"
    work = "work"


class DataType(StrEnum):
    archive = "archive"
    audio = "audio"
    chat_message = "chat_message"
    document = "document"
    email = "email"
    image = "image"
    location = "location"
    video = "video"


class Direction(StrEnum):
    incoming = "incoming"
    outgoing = "outgoing"


class FileType(StrEnum):
    unknown = "unknown"
    other = "other"
    bz2 = "bz2"
    csv = "csv"
    doc = "doc"
    docx = "docx"
    eml = "eml"
    gzip = "gzip"
    html = "html"
    image = "image"
    json = "json"
    mbox = "mbox"
    msg = "msg"
    pdf = "pdf"
    ppt = "ppt"
    pptx = "pptx"
    rar = "rar"
    sevenzip = "sevenzip"
    tar = "tar"
    tsv = "tsv"
    txt = "txt"
    video = "video"
    xls = "xls"
    xlsx = "xlsx"
    xml = "xml"
    zip = "zip"


class GeoContext(StrEnum):
    indoor = "indoor"
    outdoor = "outdoor"


class HashType(StrEnum):
    md5 = "md5"
    sha1 = "sha1"
    sha256 = "sha256"
    sha512 = "sha512"
    sha3_256 = "sha3_256"
    sha3_512 = "sha3_512"
    blake2b = "blake2b"
    blake2s = "blake2s"
    sha224 = "sha224"
    sha384 = "sha384"
    shake_128 = "shake_128"
    shake_256 = "shake_256"
    sha3_224 = "sha3_224"
    sha3_384 = "sha3_384"
    blake3 = "blake3"


Iso639_3 = StrEnum("Iso639_3", [x.part3 for x in iso639._get_all_languages() if x.part3 != "mro"])


class LocationSourceType(StrEnum):
    annotation = "annotation"
    gps = "gps"
    network = "network"


class MessageState(StrEnum):
    archived = "archived"
    deleted = "deleted"
    draft = "draft"
    flagged = "flagged"
    sent = "sent"
    spam = "spam"
    starred = "starred"
