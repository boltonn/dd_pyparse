from io import BytesIO
from pathlib import Path

import numpy as np
import pillow_avif  # noqa: F401
from loguru import logger
from PIL import ExifTags, Image, TiffImagePlugin, TiffTags
from pillow_heif import register_heif_opener

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.utils.filetype import route_mime_type

register_heif_opener()

# TODO: standardize the output of this function (namely, lat/lon) location child
# TODO: this might be an instance where it makes sense for get_file_meta to be a decorator on parse_meta


class ImageParser(FileParser):
    @staticmethod
    def get_exif(img: Image.Image, mime_type: str) -> dict:
        """Get the EXIF data from an image"""

        def _convert_gps_info(exif: dict):
            """Parse GPS info from EXIF data to decimal format"""
            gps_info = exif.get("GPSInfo")
            if gps_info is not None:
                gps_info = {ExifTags.GPSTAGS.get(key, key): value for key, value in gps_info.items()}
                if set(["GPSLatitude", "GPSLongitude", "GPSLatitudeRef", "GPSLongitudeRef"]).issubset(gps_info):
                    for axis in ["Latitude", "Longitude"]:
                        coords = gps_info[f"GPS{axis}"]
                        ref = gps_info[f"GPS{axis}Ref"]
                        axis_coord = coords[0] + coords[1] / 60 + coords[2] / 3600
                        if ref in ["S", "W"]:
                            axis_coord *= -1
                        gps_info[axis] = axis_coord
                exif["GPSInfo"] = _convert_pillow_types(gps_info)
            return exif

        def _convert_pillow_types(exif, encoding: str = None):
            """Make the output json serializable where possible"""
            out = {}
            for k, v in exif.items():
                if v is None:
                    pass

                if isinstance(v, TiffImagePlugin.IFDRational):
                    out[k] = float(v.numerator) / float(v.denominator) if v.denominator != 0 else None

                elif isinstance(v, str):
                    v = v.strip()
                    if v:
                        out[k] = v

                elif isinstance(v, (int, float)):
                    out[k] = v

                elif isinstance(v, bytes):
                    try:
                        out[k] = v.decode(encoding=encoding) if encoding is not None else v.decode()
                    except UnicodeDecodeError:
                        _ = out.pop(k, None)
                        logger.error(f"Failed to decode {k} from exif with {encoding}")

                # recurse into sub-dictionaries
                elif isinstance(v, dict):
                    out[k] = _convert_pillow_types(exif=v, encoding=encoding)

                elif isinstance(v, (tuple, list)):
                    sub_exif = {i: iter_value for i, iter_value in enumerate(v)}
                    out[k] = list(_convert_pillow_types(exif=sub_exif))

                else:
                    logger.warning(f"Cannot convert {k} from exif with type {type(v)}")
            return out

        exif = None

        if mime_type == "image/jpeg":
            if hasattr(img, "_getexif"):
                exif = img._getexif()
                if exif is not None:
                    exif = {ExifTags.TAGS[k]: v for k, v in exif.items() if k in ExifTags.TAGS}

        elif mime_type == "image/tiff":
            if hasattr(img, "tag_v2"):
                exif = img.tag_v2
                if exif is not None:
                    exif = {TiffTags.TAGS_V2[k].name: v for k, v in exif.items() if k in TiffTags.TAGS}

        else:
            raise ValueError(f"Cannot get EXIF data for {mime_type}")

        if exif:
            exif = _convert_pillow_types(exif)
            return _convert_gps_info(exif)

    @staticmethod
    def parse_meta(img: Image, mime_type: str = None) -> dict:
        """Get the shape of an image."""
        img = img.convert("RGB")
        height, width, _ = np.array(img).shape
        return {
            "height": height,
            "width": width,
            "mime_type": mime_type,
            "exif": ImageParser.get_exif(img=img, mime_type=mime_type) if mime_type in ["image/jpeg", "image/tiff"] else None,
        }

    @staticmethod
    def parse(file: Path | bytes, **kwargs):
        """Parse an image file"""
        file_name = None
        if isinstance(file, (str, Path)):
            file_name = Path(file).name
            with open(Path(file), "rb") as fb:
                file = fb.read()

        img = BytesIO(file)
        mime_type, _ = route_mime_type(file=img, file_name=file_name)

        img = Image.open(img)
        return ImageParser.parse_meta(img=img, mime_type=mime_type)
