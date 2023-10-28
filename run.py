#!/usr/bin/env python3

import sys
import datetime
from pathlib import Path
import re
from shutil import copy, copy2, copystat

from simple_term_menu import TerminalMenu

EXCLUDED_FOLDERS = [
    ".DS_Store",
]

POTENTIAL_SOURCES = [
    "/Volumes/TF Images/ASIAIR/Autorun/Light",
    "/Volumes/TF Images/ASIAIR/Plan/Light",
]

TARGET_PARENT = "/Volumes/PortableSSD/Astrophotography"
INCLUDE_PATTERN = re.compile(r"^(.+)\.((fit)|(fits))$")


def _time_str(path: Path) -> str:
    return datetime.datetime.fromtimestamp(path.stat().st_ctime).strftime("%Y-%m-%d")


def get_source_path() -> Path:
    paths = []
    for source_path in map(Path, POTENTIAL_SOURCES):
        if source_path.is_dir():
            for path in source_path.iterdir():
                if path.name not in EXCLUDED_FOLDERS:
                    paths.append(path)
    if not paths:
        print("No folders found!")
        sys.exit(1)
    paths.sort(key=lambda x: x.stat().st_ctime, reverse=True)
    idx = TerminalMenu([f"{_time_str(path)} - {path}" for path in paths]).show()
    selected_path = paths[idx]
    return selected_path


def get_target_path(source_path: Path) -> Path:
    parent_path = Path(TARGET_PARENT)
    if not parent_path.is_dir():
        print(f"Target folder {TARGET_PARENT} does not exist!")
        sys.exit(1)

    folders = []

    folders.append(
        {
            "name": "Input folder name",
            "path": None,
        }
    )

    suggested_path = parent_path.joinpath(
        f"{_time_str(source_path)} - {source_path.name}"
    )
    if not suggested_path.is_dir():
        folders.append(
            {
                "name": f"(NEW) {suggested_path.name}",
                "path": suggested_path,
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
            if path.is_file() and INCLUDE_PATTERN.match(path.name)
        ],
        key=lambda x: x.stat().st_ctime,
    )


def copy_file_if_not_exists(source_file: Path, target_file: Path) -> bool:
    if (
        target_file.is_file()
        and source_file.stat().st_size == target_file.stat().st_size
    ):
        # print(f"Skipping {source_file.name}")
        return False
    print(f"Copying {source_file.name} ...")
    copy(source_file, target_file)
    try:
        copystat(source_file, target_file)
    except PermissionError:
        # some or all permissions could not be copied. Sometimes times work and just permissions fail
        pass
    return True


def main():
    source_folder = get_source_path()
    print(f"Using source {source_folder}!")
    target_folder = get_target_path(source_folder)
    print(f"Using target {target_folder}!")
    while True:
        source_files = get_source_files(source_folder)
        for source_file in source_files:
            target_file = target_folder.joinpath(source_file.name)
            copy_file_if_not_exists(source_file, target_file)


if __name__ == "__main__":
    main()
