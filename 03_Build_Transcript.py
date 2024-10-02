"""
This script is part of a group of scripts. Please see README.MD.
Settings can be modified in settings.py
"""

import pydecima
from pydecima.resources import SentenceResource
from pydecima.enums import ETextLanguages
import os
import pandas as pd
import openpyxl
import re
from pydub import AudioSegment

import settings
from support import delete_file, file_exists, make_dir, run_command


def main() -> None:
    """
    Loops through directory, extracts subtitles from all .core files and saves it to a spreadsheet
    """

    # Set file paths
    unpacked_root = settings.UNPACKED_ROOT
    sentences_root = os.path.join(
        unpacked_root,
        "localized",
        "sentences",
    )
    pydecima.reader.set_globals(
        _game_root=unpacked_root, _decima_version=settings.DECIMA_VERSION
    )

    # Loop through directories and extract subtitles
    subtitle_list = []
    for dirpath, dirnames, filenames in os.walk(sentences_root):

        for filename in filenames:
            if filename == "sentences.core":
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(
                    os.path.join(dirpath, filename), sentences_root
                )
                subdirs = rel_path.split("\\")
                chapter = subdirs[0]
                scene = subdirs[1]

                print("Extracting scene " + abs_path)
                scene_subtitles = extract_subtitles(
                    abs_path,
                    chapter,
                    scene,
                    settings.NATIVE_LANG,
                    settings.TARGET_LANG,
                    settings.INCLUDE_AUDIO,
                    settings.CONVERTER_PATH,
                    settings.OUTPUT_FOLDER,
                    settings.UNPACKED_ROOT,
                    settings.CHAPTER_IDENTIFIERS,
                    settings.SCENE_IDENTIFIERS,
                    settings.DEFAULT_CATEGORY,
                )
                if not scene_subtitles is None:
                    subtitle_list.extend(scene_subtitles)

    # Convert to dataframe for easy manipulation and sort
    df = pd.DataFrame(subtitle_list)
    df = df.sort_values(by=["category", "chapter", "scene", "line"])

    # Output the data
    print("Writing spreadsheet")
    write_excel(
        df,
        os.path.join(
            settings.OUTPUT_FOLDER,
            f"{settings.DECIMA_VERSION}_{settings.TARGET_LANG.name}_Subtitles.xlsx",
        ),
    )

    # Write various versions of the html file
    print("Writing html")
    write_html(
        df,
        f"{settings.DECIMA_VERSION}_{settings.TARGET_LANG.name}_QuestsOnly.html",
        settings.HTML_TEMPLATE_PATH,
        settings.TARGET_LANG.name,
        settings.OUTPUT_FOLDER,
        toggle_nl="toggle",
        quests_only=True,
    )
    write_html(
        df,
        f"{settings.DECIMA_VERSION}_{settings.TARGET_LANG.name}_Toggles.html",
        settings.HTML_TEMPLATE_PATH,
        settings.TARGET_LANG.name,
        settings.OUTPUT_FOLDER,
        toggle_nl="toggle",
        quests_only=False,
    )
    write_html(
        df,
        f"{settings.DECIMA_VERSION}_{settings.TARGET_LANG.name}_AlwaysShowNative.html",
        settings.HTML_TEMPLATE_PATH,
        settings.TARGET_LANG.name,
        settings.OUTPUT_FOLDER,
        toggle_nl="shown",
        quests_only=False,
    )
    write_html(
        df,
        f"{settings.DECIMA_VERSION}_{settings.TARGET_LANG.name}_NoNL.html",
        settings.HTML_TEMPLATE_PATH,
        settings.TARGET_LANG.name,
        settings.OUTPUT_FOLDER,
        toggle_nl="off",
        quests_only=False,
    )

    print("Done! You can now move on to the next command.")


def extract_subtitles(
    file_path: str,
    chapter: str,
    scene: str,
    native_lang: ETextLanguages,
    target_lang: ETextLanguages,
    include_audio: bool,
    converter_path: str,
    output_folder: str,
    unpacked_root: str,
    chapter_categories: dict,
    scene_categories: dict,
    default_category: str,
) -> list:
    """
    Extracts native and target language subtitles from a Decima Engine .core file
    """
    scene_dict = {}
    pydecima.reader.read_objects(file_path, scene_dict)

    scene_subtitles = []
    for resource in scene_dict.values():
        if isinstance(resource, SentenceResource):
            localized_text = resource.text.follow(scene_dict)

            if localized_text is not None:

                # Extract text data
                nl_sub = clean_brackets(localized_text.language[native_lang])
                tl_sub = clean_brackets(localized_text.language[target_lang])
                category = categorise_chapters(
                    chapter,
                    scene,
                    chapter_categories,
                    scene_categories,
                    default_category,
                )
                speaker = get_speaker(resource, scene_dict, target_lang)

                if len(tl_sub) > 0:
                    line_dict = {
                        "category": category,
                        "chapter": chapter,
                        "scene": scene,
                        "line": resource.name,
                        "speaker": speaker,
                        "native_language": nl_sub,
                        "target_language": tl_sub,
                    }
                    scene_subtitles.append(line_dict)

                # Convert the audio if it exists
                if include_audio:
                    at9_path = os.path.join(
                        unpacked_root,
                        "localized",
                        "sentences",
                        chapter,
                        scene,
                        "sentences." + target_lang.name.lower(),
                        resource.name + ".at9",
                    )
                    mp3_path = os.path.join(
                        output_folder,
                        "audio",
                        chapter,
                        scene,
                        target_lang.name.lower(),
                        resource.name + ".mp3",
                    )

                    if file_exists(at9_path):
                        at9_to_mp3(converter_path, at9_path, mp3_path, False)

    return scene_subtitles


def write_excel(df: pd.DataFrame, filename: str) -> None:
    print("Writing file: " + filename)
    df.to_excel(filename, index=False)


def write_html(
    df: pd.DataFrame,
    output_filename: str,
    template_filename: str,
    target_language_name: str,
    output_folder: str,
    toggle_nl: str,
    quests_only: bool,
) -> None:

    print("Writing file: " + output_filename)

    # Generate Table of Contents data
    toc = process_toc_html(df, quests_only)

    # Generate content data
    content = process_content_html(df, target_language_name, toggle_nl, quests_only)

    # Generate instructions
    instructions = process_instructions_html(toggle_nl)

    # Merge data into template
    template_text = merge_template_html(template_filename, toc, content, instructions)

    write_file_html(os.path.join(output_folder, output_filename), template_text)


def write_file_html(output_filename: str, template_text: str) -> None:
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(template_text)


def merge_template_html(
    template_filename: str, toc: str, content: str, instructions: str
) -> str:

    with open(template_filename, "r") as file:
        template_text = file.read()

    template_text = template_text.replace("{{INSERT_TOC_HERE}}", toc, 1)
    template_text = template_text.replace("{{INSERT_CONTENT_HERE}}", content, 1)
    template_text = template_text.replace(
        "{{INSERT INSTRUCTIONS HERE}}", instructions, 1
    )

    return template_text


def process_instructions_html(toggle_nl: str) -> str:
    instructions = ""

    if toggle_nl == "toggle":
        instructions = "Click on the speaker's name to hear the audio or click on the sentence to get the translation"
    else:
        instructions = "Click on the speaker's name to hear the audio"

    return instructions


def process_content_html(
    df: pd.DataFrame, target_language_name: str, toggle_nl: str, quests_only: bool
) -> str:
    content_data = ""
    previous_chapter_code = "[start_of_loop]"
    previous_scene = "[start_of_loop]"

    for index, row in df.iterrows():
        category = row["category"]
        chapter = row["chapter"]
        scene = row["scene"]
        speaker = row["speaker"]
        line = row["line"]
        tl_sub = row["target_language"]
        nl_sub = row["native_language"]
        chapter_code = create_chapter_code(category, chapter)
        audio_html_path = (
            "audio"
            + "/"
            + chapter
            + "/"
            + scene
            + "/"
            + target_language_name.lower()
            + "/"
            + line
            + ".mp3"
        )

        # Move on to the next one if we have quests only enabled and the category is not a quest
        if quests_only:
            category_code = int(category[0:2])

            if category_code >= 10:
                continue

        # Make line compatible with css, now that we have used the "correct" version with the audio path
        line = spaces_to_underscores(line.strip())

        # Deal with chapter and categories changing
        if chapter_code != previous_chapter_code:
            # End the previous chapter
            if previous_chapter_code != "[start_of_loop]":
                content_data += "</tbody></table></div></article></section>\n"

            # Start new chapter
            content_data += f'<section id="{chapter_code}"><div class="row"><h1 class="col">{chapter}</h1></div>\n'

            # Update data for next iteration of loop
            previous_chapter_code = chapter_code

        # Deal with scene changing
        if scene != previous_scene:
            # End the previous scene
            if previous_chapter_code != "[start_of_loop]":
                content_data += "</tbody></table></div></article>\n"

            # Start new scene
            content_data += f'<article class="row" id="{scene}"><div class="col"><h2 class="fw-lighter text-body-secondary">{scene}</h2><table class="table table-borderless table-sm"><thead><th style="width: 10%"></th><th></th></thead><tbody>\n'

            # Update data for next iteration of loop
            previous_scene = scene

        # Add in the current line
        if toggle_nl == "toggle":
            content_data += (
                '<tr><th onclick="playAudio('
                + f"'{audio_html_path}'"
                + f')">{speaker}</th><td><span data-bs-toggle="collapse" role="button" href="#{line}">{tl_sub}</span><div class="collapse fw-lighter text-body-secondary fst-italic" id="{line}">{nl_sub}</div></td></tr>\n'
            )
        elif toggle_nl == "shown":
            content_data += (
                '<tr><th onclick="playAudio('
                + f"'{audio_html_path}'"
                + f')">{speaker}</th><td><span>{tl_sub}</span><div class="fw-lighter text-body-secondary fst-italic" id="{line}">{nl_sub}</div></td></tr>\n'
            )
        else:
            content_data += (
                '<tr><th onclick="playAudio('
                + f"'{audio_html_path}'"
                + f')">{speaker}</th><td>{tl_sub}</td></tr>\n'
            )

    # Terminate final scene and chapter
    content_data += "</tbody></table></div></article></section>\n"

    return content_data


def process_toc_html(df: pd.DataFrame, quests_only: bool) -> str:
    toc_data = ""
    previous_category = "[start_of_loop]"
    for category in df["category"].unique():

        # Move on to the next one if we have quests only enabled and the category is not a quest
        if quests_only:
            category_code = int(category[0:2])

            if category_code >= 10:
                continue

        for chapter in df[df["category"] == category]["chapter"].unique():
            # Deal with categories first
            if category != previous_category:
                # End the previous category
                if previous_category != "[start_of_loop]":
                    toc_data += "</ul></li>\n"

                # Start new category
                toc_data += f'<a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">{category}</a><ul class="dropdown-menu">\n'

                # Update data for next iteration of loop
                previous_category = category

            # Add in the chapters
            chapter_code = create_chapter_code(category, chapter)
            toc_data += f'<li><a class="dropdown-item" href="#{chapter_code}">{chapter}</a></li>\n'

    # Terminate final category
    toc_data += "</ul></li>\n"

    return toc_data


def create_chapter_code(category: str, chapter: str) -> str:
    chapter_code = spaces_to_underscores(category + "_" + chapter).strip()

    return chapter_code


def spaces_to_underscores(input_str: str) -> str:
    output = input_str.replace(" ", "_")

    return output


def categorise_chapters(
    chapter: str,
    scene: str,
    chapter_identifiers: dict,
    scene_identifiers: dict,
    default_category: str,
) -> str:

    # Default is other. Overwrite with chapter if found and further overwrite with scene if found
    category = default_category

    for ci in chapter_identifiers.keys():
        if chapter.startswith(ci):
            category = chapter_identifiers[ci]
            break

    for si in scene_identifiers.keys():
        if si in scene:
            category = scene_identifiers[si]
            break

    return category


def get_speaker(
    resource: SentenceResource, scene_dict: dict, target_lang: ETextLanguages
) -> str:
    """
    Work out the speaker's name in the target language for a given line
    """

    # Take a local copy as it will be modified
    scene_dict_local = scene_dict.copy()

    # Work out the name but default to English if it can't be found in the target language
    voice_str = ""

    try:
        voice_name = resource.voice.follow(scene_dict_local).text.follow(
            scene_dict_local
        )
        if voice_name.language[target_lang] != "":
            voice_str = voice_name.language[target_lang]
        elif voice_name.language[ETextLanguages.English] != "":
            voice_str = voice_name.language[ETextLanguages.English]
    except:
        voice_str = "<No voice name>"

    return voice_str


def clean_brackets(input_string: str) -> str:
    """
    Removes all text within angled brackets from the input string.
    """
    return re.sub(r"<.*?>", "", input_string)


def at9_to_mp3(
    converter_path: str, input_file: str, output_file: str, print_output: bool
) -> None:

    temp_file = "temp.wav"

    # Convert at9 to wav
    run_command([converter_path, input_file, temp_file], print_output)

    # Wav to mp3
    make_dir(output_file)
    AudioSegment.from_wav(temp_file).export(output_file, format="mp3")

    # Delete wav
    delete_file(temp_file)


if __name__ == "__main__":
    main()
