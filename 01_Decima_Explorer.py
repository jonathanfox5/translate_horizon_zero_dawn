"""
This script is part of a group of scripts. Please see README.MD.
Settings can be modified in settings.py
"""

import os

import settings
from support import run_command, copy_file, file_exists


def main():
    # Get files
    dll_name = "oo2core_3_win64.dll"
    dll_path = os.path.join(settings.GAME_ROOT, dll_name)
    decima_explorer_root, decima_explorer_exe = os.path.split(
        settings.DECIMA_EXPLORER_PATH
    )

    # Check that the dll is in the game path
    if not file_exists(dll_path):
        print(
            f"[ERROR] Could not copy {dll_name} to {decima_explorer_root} from {settings.GAME_ROOT}. Is there a similarly named dll that you can manually copy instead?\nOnce you have, you can launch {decima_explorer_exe} manually from {decima_explorer_root}"
        )
        exit()

    # Copy the file
    copy_file(source_path=dll_path, target_path=decima_explorer_root)

    # Launch decima explorer
    run_command(settings.DECIMA_EXPLORER_PATH)

    print("Done! You can now move on to the next command.")


if __name__ == "__main__":
    main()
