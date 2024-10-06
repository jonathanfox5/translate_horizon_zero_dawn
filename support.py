import os
import subprocess
import shutil


def run_command(command_list: list, print_output: bool = True) -> None:

    if print_output:
        print("Command:" + " ".join(command_list))

    result = subprocess.run(command_list, capture_output=True, text=True)

    if print_output:
        print(result.stdout)
        print(result.stderr)


def run_py_script(command_list: list, print_output: bool = True) -> None:

    if print_output:
        print("Command:" + " ".join(command_list))

    result = subprocess.run(command_list, stdout=subprocess.PIPE, shell=True)

    if print_output:
        print(result.stdout)
        print(result.stderr)


def copy_file(source_path, target_path):
    try:
        shutil.copy(source_path, target_path)
        print(f"File copied from {source_path} to {target_path}")
    except Exception as e:
        print(f"Error: {e}")


def delete_file(filename: str) -> bool:
    if not file_exists(filename):
        return False

    try:
        os.remove(filename)
        return True
    except:
        return False


def folder_exists(path: str) -> bool:
    folder, file = os.path.split(path)
    return os.path.isdir(folder)


def make_dir(path: str) -> None:
    folder, file = os.path.split(path)
    if not folder_exists(folder):
        os.makedirs(folder)


def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)


def get_script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def decima_lang_to_simplemma(decima_lang: str) -> str:
    """Only covers european languages to match lemmatizer"""

    lookup = {
        "English": "en",
        "French": "fr",
        "Spanish": "es",
        "German": "de",
        "Italian": "it",
        "Dutch": "nl",
        "Portuguese": "pt",
        "TraditionalChinese": "",
        "Korean": "",
        "Russian": "ru",
        "Polish": "pl",
        "Danish": "da",
        "Finnish": "fi",
        "Norwegian": "nb",
        "Swedish": "sv",
        "Japanese": "",
        "LatinAmericanSpanish": "es",
        "BrazilianPortuguese": "pt",
        "Turkish": "",
        "Arabic": "tr",
        "SimplifiedChinese": "",
    }

    output = lookup[decima_lang]

    return output
