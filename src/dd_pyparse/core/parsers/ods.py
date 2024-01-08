import tempfile
from pathlib import Path

from dd_pyparse.core.parsers.base import FileParser
from dd_pyparse.core.parsers.xlsx import XlsxParser
from dd_pyparse.core.utils.externals import convert_with_libre


class OdsParser(FileParser):
    """Parse a doc file by converting it to docx and then using the docx parser
    
        Supported formats: ods
    """
    @staticmethod
    def parse(
        file: Path | bytes,
        cleaned: bool = True,
        **kwargs,
    ) -> dict:
        if isinstance(file, (Path, str)):
            file_path = Path(file)

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = convert_with_libre(
                    file_path=file_path,
                    tmp_dir=tmp_dir,
                    target_format="xlsx",
                )

                return XlsxParser.parse(
                    file=tmp_path,
                    cleaned=cleaned,
                    **kwargs,
                )

        elif isinstance(file, bytes):
            with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp_file:
                tmp_file.write(file)
                return XlsxParser.parse(
                    file=tmp_file.name,
                    cleaned=cleaned,
                    **kwargs,
                )
