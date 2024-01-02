import subprocess
from pathlib import Path

from loguru import logger


def convert_with_libre(file_path: Path, tmp_dir: Path, target_format: str):
    """Convert a file to a target format using libreoffice

    Note: This is meant to be used as a fallback against temp files or
    directories since LibreOffice does not have permission to write to
    anywhere other than the /tmp directory and it is slow.
    """
    out_path = Path(tmp_dir) / f"{file_path.stem}.{target_format}"
    logger.debug(f"Converting {file_path.stem} to {target_format=} at: {out_path}")
    command = [
        "soffice",
        "--headless",
        "--convert-to",
        target_format,
        "--outdir",
        str(tmp_dir),
        str(file_path),
    ]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process.communicate()
    except FileNotFoundError:
        raise FileNotFoundError("LibreOffice is not installed")

    if process.returncode != 0:
        logger.error(stderr.decode().strip())
        raise RuntimeError(f"LibreOffice failed to convert {file_path} to {target_format}")

    return out_path
