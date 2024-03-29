from multiprocessing import JoinableQueue, Process
from pathlib import Path
from typing import Type

from dd_pyparse.core.parsers import route_parser
from dd_pyparse.core.parsers.base import (FileParser, FileStreamer,
                                          get_file_meta)
from dd_pyparse.schemas.base import Base
from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import FileType
from dd_pyparse.utils.logging import logger


class Processor:
    def __init__(
        self,
        in_dir: Path,
        children_dir: Path,
        out_dir: Path,
        dataset: str,
        num_workers: int,
        extract_children: bool = False,
        pattern: str = "*",
        **kwargs,
    ):
        self.in_dir = in_dir
        self.children_dir = children_dir
        self.out_dir = out_dir
        self.dataset = dataset
        self.num_workers = num_workers
        self.extract_children = extract_children
        self.pattern = pattern
        self.kwargs = kwargs

        self.queue = JoinableQueue()

    def _get_files(self):
        num_files = 0
        logger.info(f"Searching for files in {self.in_dir}")
        for file_path in self.in_dir.rglob(self.pattern):
            if file_path.is_file():
                self.queue.put(File(absolute_path=str(file_path)))
                num_files += 1
        logger.info(f"Found {num_files} files")

    def _handle_child(self, child: Type[Base]):
        if child.__repr_name__() == "File":
            logger.debug(f"Putting file {child.absolute_path} in queue")
            self.queue.put(child)
        else:
            logger.debug(f"Writing {child}")
            self.write(child)

    def _process(self, file: Type[File]):
        """Process a file"""
        out = get_file_meta(file.absolute_path)
        file_type = out.get("file_type")
        
        if file_type in [FileType.unknown]:
            logger.warning(f"Could not determine file type for {file.absolute_path=}, {file_type=}")
            # keep reference to file
            self.write(File(**out))
            return
        
        parser, validator = route_parser(file_type)

        if parser.__base__ == FileParser:
            out |= parser.parse(file=file.absolute_path, extract_children=self.extract_children, out_dir=self.children_dir, **self.kwargs)

            out = out | file.model_dump(mode="dict", exclude_none=True)
            out = validator(**out)
            if out.children and self.extract_children:
                for child in out.children:
                    self._handle_child(child)
                del out.children
            self.write(out)

        elif parser.__base__ == FileStreamer:
            for child in parser.stream(file_path=file.absolute_path, extract_children=self.extract_children, out_dir=self.children_dir, **self.kwargs):
                child.parent_id = file.id
                if child.children and self.extract_children:
                    for _child in child.children:
                        self._handle_child(_child)
                    del child.children
                self._handle_child(child)

            out = out | file.model_dump(mode="dict", exclude_none=True)
            out = validator(**out)
            self.write(out)

        else:
            raise TypeError(f"Cannot parse {file_type}")

    def _worker(self):
        while True:
            # get file from queue and make sure other workers don't process it
            file = self.queue.get()
            if file is None:
                break
            try:
                
                self._process(file)
            except Exception as e:
                logger.error(f"Error processing {file.absolute_path}: {e}")
            finally:
                self.queue.task_done()

    def run(self):
        """Run the processor"""
        logger.info(f"Starting {self.num_workers} workers")
        workers = []
        for _ in range(self.num_workers):
            worker = Process(target=self._worker)
            worker.start()
            workers.append(worker)

        self._get_files()
        self.queue.join()

        logger.info("Stopping workers")
        for _ in range(self.num_workers):
            self.queue.put(None)
        for worker in workers:
            worker.join()

    def write(self, data: Type[File]):
        """Write a file to the filesystem"""
        out_path = self.out_dir / f"{data.id}.json"
        with open(out_path, "w") as fb:
            out = data.model_dump_json(exclude_none=True, by_alias=True, indent=4)
            fb.write(out)
        logger.debug(f"Wrote {out_path}")


def process(
    in_dir: Path,
    children_dir: Path,
    out_dir: Path,
    dataset: str,
    num_workers: int,
    extract_children: bool = False,
    pattern: str = "*",
    **kwargs,
):
    """Process files"""
    out_dir.mkdir(parents=True, exist_ok=True)

    processor = Processor(
        in_dir=in_dir,
        children_dir=children_dir,
        out_dir=out_dir,
        dataset=dataset,
        num_workers=num_workers,
        extract_children=extract_children,
        pattern=pattern,
        **kwargs,
    )
    processor.run()


def main():
    import argparse

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser(description="Process files")
    parser.add_argument("--in_dir", type=Path, help="Input directory", required=True, default=None)
    parser.add_argument(
        "--children_dir",
        type=Path,
        help="Children directory",
        default=None,
    )
    parser.add_argument("--out_dir", type=Path, help="Output directory", required=True, default=None)
    parser.add_argument("--dataset", type=str, help="Dataset", required=True, default=None)
    parser.add_argument("--num_workers", type=int, help="Number of workers", required=True, default=None)
    parser.add_argument("--extract_children", type=str2bool, default=True, help="Extract children")
    parser.add_argument("--pattern", type=str, help="Pattern", required=False, default="*")
    args = parser.parse_args()
    logger.info(f"Running with {args=}")
    if args.extract_children and not args.children_dir:
        raise ValueError("Must provide children_dir if extract_children is True")

    process(
        in_dir=args.in_dir,
        children_dir=args.children_dir,
        out_dir=args.out_dir,
        dataset=args.dataset,
        num_workers=args.num_workers,
        extract_children=args.extract_children,
        pattern=args.pattern,
    )

if __name__ == "__main__":
    main()