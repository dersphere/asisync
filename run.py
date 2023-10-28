#!/usr/bin/env python3

import sys
import datetime
from pathlib import Path

from simple_term_menu import TerminalMenu

EXCLUDED_FOLDERS = [
    '.DS_Store',
]

POTENTIAL_SOURCES = [
    '/Volumes/TF Images/ASIAIR/Autorun/Light',
    '/Volumes/TF Images/ASIAIR/Plan/Light',
]

TARGET_PARENT = '/Volumes/PortableSSD/Astrophotography'

def _time_str(path: Path) -> str:
    return datetime.datetime.fromtimestamp(path.stat().st_ctime).strftime('%Y-%m-%d')

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
    idx = TerminalMenu([f'{_time_str(path)} - {path}' for path in paths]).show()
    selected_path = paths[idx]
    return selected_path



def get_target_path(source_path: Path) -> Path:
    parent_path = Path(TARGET_PARENT)
    if not parent_path.is_dir():
        print(f"Target folder {TARGET_PARENT} does not exist!")
        sys.exit(1)

    folders = []

    folders.append({
        'name': 'Input folder name',
        'path': None,
    })

    suggested_path = parent_path.joinpath(f'{_time_str(source_path)} - {source_path.name}')
    if not suggested_path.is_dir():
        folders.append({
            'name': f'(NEW) {suggested_path.name}' ,
            'path': suggested_path,
        })

    folders.extend([{
        'name': path.name,
        'path': path,
    } for path in sorted(parent_path.iterdir(), key=lambda x: x.stat().st_ctime, reverse=True) if not path.name in EXCLUDED_FOLDERS])

    idx = TerminalMenu([folder["name"] for folder in folders]).show()
    selected_folder = folders[idx]
    if selected_folder['path'] is None:
        new_folder_name = input("Enter new folder name: ")
        target_path = parent_path.joinpath(new_folder_name)
    else:
        target_path = selected_folder['path']
    if not target_path.is_dir():
        target_path.mkdir()
    return target_path

def main():
    source_folder = get_source_path()
    print(f"Using source {source_folder}!")
    target_folder = get_target_path(source_folder)
    print(f"Using target {target_folder}!")

if __name__ == "__main__":
    main()
