#!/usr/bin/env python3

import shutil
import os
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

def _time_str(file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d')

def get_source_folder():
    folders = []
    for source in POTENTIAL_SOURCES:
        if os.path.exists(source):
            for folder in os.listdir(source):
                if folder not in EXCLUDED_FOLDERS:
                    folders.append({
                        'name': folder,
                        'path': os.path.join(source, folder),
                        'date': _time_str(os.path.join(source, folder)),
                    })
    if not folders:
        print("No folders found!")
        sys.exit(1)
    folders.sort(key=lambda x: x['date'], reverse=True)
    folders_menu = [f'{folder["date"]} - {folder["path"]}' for folder in folders]
    idx = TerminalMenu(folders_menu).show()
    selected_folder = folders[idx]
    return selected_folder

def get_target_folder(source_folder):
    if not os.path.exists(TARGET_PARENT):
        print(f"Target folder {TARGET_PARENT} does not exist!")
        sys.exit(1)

    folders = []

    folders.append({
        'name': 'Create new folder',
        'path': None,
    })

    potential_target_folder_name = f'{source_folder["date"]} - {source_folder["name"]}'
    new_str = ' (NEW)' if not os.path.exists(os.path.join(TARGET_PARENT, potential_target_folder_name)) else ''
    folders.append({
        'name': f'{potential_target_folder_name}{new_str}' ,
        'path': os.path.join(TARGET_PARENT, potential_target_folder_name),
    })

    folders.extend([{
        'name': folder.name,
        'path': os.path.join(TARGET_PARENT, folder),
    } for folder in sorted(Path(TARGET_PARENT).iterdir(), key=os.path.getctime, reverse=True)])

    folders_menu = [folder["name"] for folder in folders]
    idx = TerminalMenu(folders_menu).show()
    selected_folder = folders[idx]
    if selected_folder['path'] is None:
        new_folder_name = input("Enter new folder name: ")
        selected_folder = {
            'name': new_folder_name,
            'path': os.path.join(TARGET_PARENT, new_folder_name),
        }
        os.mkdir(selected_folder['path'])
    return selected_folder

def main():
    #source_folder = get_source_folder()
    source_folder = {'name': 'NGC188', 'path': '/Volumes/TF Images/ASIAIR/Autorun/Light/NGC188', 'date': '2023-10-27'}
    print(f"Using source {source_folder}!")
    target_folder = get_target_folder(source_folder)
    print(f"Using target {target_folder}!")

if __name__ == "__main__":
    main()
