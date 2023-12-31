#!/usr/bin/env python3

from datetime import datetime, timedelta
import re
import sys
import time
from pathlib import Path
from shutil import copystat

from simple_term_menu import TerminalMenu

SLEEP_SECSONDS = 30
FILE_CTIME_MIN_SECONDS = 10


SOURCE_FOLDERS = [
    "/Volumes/TF Images/ASIAIR/Autorun/Light",
    "/Volumes/TF Images/ASIAIR/Plan/Light",
]
TARGET_PARENT_FOLDER = "/Volumes/PortableSSD/Astrophotography"

TARGET_SUBFOLDER = "lights"
TARGET_SUBFOLDER_ALTERNATIVE = "lights/trash"

EXCLUDED_FOLDERS = [
    ".DS_Store",
]
FILE_INCLUDE_PATTERN = re.compile(r"^(.+)\.((fit)|(fits))$")


def _date_str(path: Path) -> str:
    # remove 12h to get the date of the night
    return (
        datetime.fromtimestamp(path.stat().st_ctime) - timedelta(hours=12)
    ).strftime("%Y-%m-%d")


def _copy_file_with_progress(
    source_file: Path, destination_file: Path, chunk_size=1024 * 64
) -> None:
    total_size = source_file.stat().st_size
    with open(source_file, "rb") as src_file, open(destination_file, "wb") as dest_file:
        copied_size = 0
        while True:
            data = src_file.read(chunk_size)
            if not data:
                break
            dest_file.write(data)
            copied_size += len(data)
            progress = int(
                (copied_size / total_size) * 50
            )  # 50 characters in the progress bar
            print(
                f"Copying {source_file.name} ... [{'#' * progress}{' ' * (50 - progress)}] {100 * copied_size // total_size}%\r",
                end="",
                flush=True,
            )
    try:
        copystat(source_file, destination_file)
    except PermissionError:
        # some or all permissions could not be copied. Sometimes times work and just permissions fail
        pass
    print("")


def get_source_path() -> Path:
    paths = []
    for source_path in map(Path, SOURCE_FOLDERS):
        if source_path.is_dir():
            for path in source_path.iterdir():
                if path.name not in EXCLUDED_FOLDERS:
                    paths.append(path)
    if not paths:
        print("No folders found!")
        sys.exit(1)
    paths.sort(key=lambda x: x.stat().st_ctime, reverse=True)
    idx = TerminalMenu([f"{_date_str(path)} - {path}" for path in paths]).show()
    selected_path = paths[idx]
    return selected_path


def get_target_path(source_path: Path) -> Path:
    parent_path = Path(TARGET_PARENT_FOLDER)
    if not parent_path.is_dir():
        print(f"Target folder {TARGET_PARENT_FOLDER} does not exist!")
        sys.exit(1)

    folders = []

    # add suggested path as the first entry - could already exist or not
    suggested_path = parent_path.joinpath(
        f"{_date_str(source_path)} - {source_path.name}"
    )
    folders.append(
        {
            "name": f"(NEW) {suggested_path.name}"
            if not suggested_path.is_dir()
            else suggested_path.name,
            "path": suggested_path,
        }
    )

    # add interactive input as the second entry
    folders.append(
        {
            "name": "Input folder name",
            "path": None,
        }
    )

    folders.extend(
        [
            {
                "name": path.name,
                "path": path,
            }
            for path in sorted(
                parent_path.iterdir(), key=lambda x: x.stat().st_ctime, reverse=True
            )
            if not path.name in EXCLUDED_FOLDERS
            and not path.name == suggested_path.name
        ]
    )

    idx = TerminalMenu([folder["name"] for folder in folders]).show()
    selected_folder = folders[idx]
    if selected_folder["path"] is None:
        new_folder_name = input("Enter new folder name: ")
        target_path = parent_path.joinpath(new_folder_name)
    else:
        target_path = selected_folder["path"]
    if not target_path.is_dir():
        target_path.mkdir()
    return target_path


def get_source_files(source_path: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in source_path.iterdir()
            if path.is_file() and FILE_INCLUDE_PATTERN.match(path.name)
        ],
        key=lambda x: x.stat().st_ctime,
    )


def handle_file(source_file: Path, target_path: Path) -> bool:
    target_file = target_path.joinpath(TARGET_SUBFOLDER).joinpath(source_file.name)
    alternative_target_file = target_path.joinpath(
        TARGET_SUBFOLDER_ALTERNATIVE
    ).joinpath(source_file.name)
    if (
        (
            target_file.is_file()
            and source_file.stat().st_size == target_file.stat().st_size
        )
        or alternative_target_file.is_file()
        or source_file.stat().st_ctime > time.time() - FILE_CTIME_MIN_SECONDS
    ):
        return False
    if not target_file.parent.is_dir():
        target_file.parent.mkdir(parents=True)
    _copy_file_with_progress(source_file, target_file)
    return True


def main():
    source_folder = get_source_path()
    target_folder = get_target_path(source_folder)
    print(f"Using source {source_folder}!")
    print(f"Using target {target_folder}!")
    while True:
        try:
            for source_file in get_source_files(source_folder):
                handle_file(source_file, target_folder)
            print("Waiting for new files ... (Ctrl+C to exit)")
            time.sleep(SLEEP_SECSONDS)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
