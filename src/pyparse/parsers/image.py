from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

from pyparse.parsers.file import FileParser


class ImageParser:
    @staticmethod
    def parse(img: Path | bytes, return_img: bool = False):
        if isinstance(img, str):
            img = Path(img)

        if isinstance(img, Path):
            with open(img, "rb") as fb:
                img = fb.read()

        meta = FileParser.parse_bytes(img)
        img = np.array(Image.open(BytesIO(img)).convert("RGB"))
        height, width, _ = img.shape
        meta |= {"height": height, "width": width}
        if return_img:
            return meta, img
        return meta
