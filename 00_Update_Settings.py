"""
This script is part of a group of scripts. Please see README.MD.
Settings can be modified in settings.py
"""

from support import run_command


def main():
    # Open settings.py
    command = ["notepad.exe", "settings.py"]
    run_command(command)

    print("Done! You can now move on to the next command.")


if __name__ == "__main__":
    main()
