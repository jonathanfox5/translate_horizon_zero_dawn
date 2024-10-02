"""
This script is part of a group of scripts. Please see README.MD.
Settings can be modified in settings.py
"""

import os

import settings
import pydecima

from support import file_exists, get_script_dir, run_py_script


def main() -> None:

    # Get paths and write the relevant settings to the appropriate directory
    print("Setting paths for dump script")
    working_directory = get_script_dir()
    sentence_dumper_root = settings.SENTENCE_DUMPER_PATH
    sentence_dumper_settings = os.path.join(sentence_dumper_root, "hzd_root_path.txt")
    game_root = settings.GAME_ROOT
    tl_name = settings.TARGET_LANG.name
    unpacked_root = os.path.join(working_directory, settings.UNPACKED_ROOT)
    decima_explorer_cli = os.path.join(working_directory, settings.DECIMA_EXPLORER_CLI)
    sentences_root = os.path.join(unpacked_root, "localized", "sentences")

    with open(sentence_dumper_settings, "w") as file:
        file.write(unpacked_root)

    print("Dumping files, this may take a while")

    # Dump Initial, Remainder and DLC1 bin files
    bin_list = ["Initial", "Remainder", "DLC1"]

    for bin_name in bin_list:
        bin_path = os.path.join(
            game_root, "Packed_DX12", bin_name + "_" + tl_name + ".bin"
        )
        print(f"Extracting {bin_path}")

        if file_exists(bin_path):
            # Example command from decima-scripts documentation:
            # python dump_language_streams.py "E:\Games\SteamApps\common\Horizon Zero Dawn\Packed_DX12\Initial_English.bin" "C:\Tools\Decima Explorer\DecimaExplorer.exe"
            command = [
                "python",
                os.path.join(sentence_dumper_root, "dump_language_streams.py"),
                bin_path,
                decima_explorer_cli,
            ]
            run_py_script(command)
        else:
            print(
                f"{bin_path} does not appear to exist. Your language may not be supported as audio by the name"
            )

    # Extract the at9 files
    # Example command from decima-scripts documentation:
    # python sentence_dumper.py "C:\HZD\localized\sentences\aigenerated"
    # Note that -l [Languagename] is also required for any language that isn't english
    command = [
        "python",
        os.path.join(sentence_dumper_root, "sentence_dumper.py"),
        sentences_root,
        "-l",
        tl_name,
    ]
    run_py_script(command)

    print("Done! You can now close this window.")


if __name__ == "__main__":
    main()
