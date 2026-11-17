from multiprocessing import Process, Manager, current_process
import logging
import sys
from pathlib import Path
import shutil

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def copy_file(file_path, destination_dir, result_dict):
    name = current_process().name
    logger.debug(f"Started copy: {name} -> {file_path}")

    extension = file_path.suffix[1:].lower()
    if not extension:
        extension = "no_extension"

    target_folder = destination_dir / extension
    target_folder.mkdir(parents=True, exist_ok=True)

    target_file = target_folder / file_path.name
    shutil.copy2(file_path, target_file)

    result_dict[str(file_path)] = str(target_file)
    logger.debug(f"Done copy: {name} -> {target_file}")


def process_directory(source_dir, destination_dir, result_dict):
    name = current_process().name
    logger.debug(f"Scanning: {source_dir} by {name}")

    processes = []

    for item in source_dir.iterdir():
        if item.is_dir():
            pr = Process(target=process_directory, args=(
                item, destination_dir, result_dict))
            pr.start()
            processes.append(pr)

        elif item.is_file():
            pr = Process(target=copy_file, args=(
                item, destination_dir, result_dict))
            pr.start()
            processes.append(pr)

    for pr in processes:
        pr.join()

    logger.debug(f"Finished scanning: {source_dir} by {name}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_dir> [destination_dir]")
        sys.exit(1)

    source_dir = Path(sys.argv[1])

    if len(sys.argv) > 2:
        destination_dir = Path(sys.argv[2])
    else:
        destination_dir = Path("dist")

    if not source_dir.exists() or not source_dir.is_dir():
        print("Source directory does not exist")
        sys.exit(1)

    destination_dir.mkdir(parents=True, exist_ok=True)

    with Manager() as manager:
        result_dict = manager.dict()

        pr = Process(target=process_directory, args=(
            source_dir, destination_dir, result_dict))
        pr.start()
        pr.join()

        print(dict(result_dict))
