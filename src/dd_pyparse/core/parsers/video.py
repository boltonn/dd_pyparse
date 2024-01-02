import os
from pathlib import Path

import cv2

from dd_pyparse.core.parsers.base import FileParser


class VideoParser(FileParser):
    @staticmethod
    def check_is_variable_fps(file_path: Path) -> bool:
        """Check if video has variable fps"""
        return os.popen("ffmpeg -i in -vf vfrdet -an -f full -y /dev/null").read().strip() == "Variable Frame Rate Detected"

    @staticmethod
    def get_duration(file_path: Path) -> float:
        """Get video duration"""
        return float(
            os.popen(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_path}").read().strip()
        )

    @staticmethod
    def parse(
        file: Path,
        **kwargs,
    ) -> dict:
        """Parse a video file"""

        cap = cv2.VideoCapture(str(file))
        return {
            "height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
            "width": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "num_frames": cap.get(cv2.CAP_PROP_FRAME_COUNT),
            "is_variable_fps": VideoParser.check_is_variable_fps(file),
            "duration": VideoParser.get_duration(file),
        }
