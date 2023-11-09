from enum import Enum


class DataType(Enum):
    audio = "audio"
    chat = "chat"
    document = "document"
    email = "email"
    image = "image"
    video = "video"


class FileType(Enum):
    docx = "docx"
    eml = "eml"
    img = "img"
    txt = "txt"


class Hash(Enum):
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

