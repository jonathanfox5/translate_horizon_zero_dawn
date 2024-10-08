"""
This script is part of a group of scripts. Please see README.MD.
Settings can be modified in settings.py
"""

import os
import html
import random
import json
import re

import pandas as pd
import genanki

import settings
from tools.lemon_tizer.lemon_tizer import LemonTizer
from support import decima_lang_to_simplemma


def main() -> None:

    input_spreadsheet = os.path.join(
        settings.OUTPUT_FOLDER,
        f"{settings.DECIMA_VERSION}_{settings.TARGET_LANG.name}_Subtitles.xlsx",
    )
    df_input = pd.read_excel(input_spreadsheet)

    df_freq = frequency_analysis(
        df_input=df_input,
        target_language_name=settings.TARGET_LANG.name,
        target_language_abbreviation=decima_lang_to_simplemma(
            settings.TARGET_LANG.name
        ),
        wiki_freq_spreadsheet_path=settings.GENERAL_1000_WORDS_PATH,
        output_directory=settings.OUTPUT_FOLDER,
        game_name=settings.DECIMA_VERSION,
        exclude_list=settings.ANKI_EXCLUDE,
        max_cards=settings.ANKI_MAX_CARDS,
        lemmatize_words=settings.LEMMATIZE_WORDS,
    )

    build_anki_deck(
        df=df_freq,
        target_language_name=settings.TARGET_LANG.name,
        template_directory=settings.ANKI_TEMPLATE_DIRECTORY,
        output_directory=settings.OUTPUT_FOLDER,
        game_name=settings.DECIMA_VERSION,
        dictionary_path=settings.DICTIONARY_PATH,
        word_audio_root=settings.WORD_AUDIO_PATH,
    )

    print("Done! You can now close this window.")


def build_anki_deck(
    df: pd.DataFrame,
    target_language_name: str,
    template_directory: str,
    output_directory: str,
    game_name: str,
    dictionary_path: str,
    word_audio_root: str,
) -> None:

    print("Create Anki: Setting up")

    # Work out paths, etc.
    deck_name = game_name + "_" + target_language_name
    deck_output_path = os.path.join(output_directory, deck_name + ".apkg")
    css_path = os.path.join(template_directory, "anki_card.css")
    front_path = os.path.join(template_directory, "front.html")
    back_path = os.path.join(template_directory, "back.html")
    model_fields_path = os.path.join(template_directory, "fields.json")

    # Load dictionary
    dictionary = load_json(dictionary_path)

    # Create model
    model_fields = load_json(model_fields_path)
    model_name = deck_name

    model_template = [
        {
            "name": model_name,
            "qfmt": read_file_to_string(front_path),
            "afmt": read_file_to_string(back_path),
        },
    ]

    model = create_model(
        model_id=generate_anki_id(),
        model_name=model_name,
        fields=model_fields,
        template=model_template,
        css=read_file_to_string(css_path),
    )

    print("Create Anki: Creating cards (may take a while)")

    # Create the individual cards
    i = 0
    note_cards = []
    media_files = []
    for _, row in df.iterrows():
        # Get data from row
        word = str(row["word"]).lower()
        line = str(row["line"])
        speaker = str(row["speaker"])
        tl_sub = str(row["target_language"])
        nl_sub = str(row["native_language"])
        chapter = str(row["chapter"])
        scene = str(row["scene"])
        word_frequency = str(row["frequency"])
        card_index = str(i)

        # Look up the definition but don't sanitise
        definition = find_definition(dictionary, word)

        # Put the file names for the audio into Anki card format
        sentence_audio_field_anki = sanitise_string_html(
            format_audio_field(line + ".mp3")
        )
        word_audio_field_anki = sanitise_string_html(format_audio_field(word + ".mp3"))

        # Get the paths of the sentence and word audio so that they can be packaged
        sentence_audio_path = get_audio_filepath(
            output_folder=output_directory,
            chapter=chapter,
            scene=scene,
            line=line,
            target_language_name=target_language_name,
        )
        word_audio_path = find_file(word_audio_root, word + ".mp3")

        # Set the field values for the card
        note_fields = [
            card_index,
            sanitise_string_html(word),
            sanitise_string_html(speaker),
            sanitise_string_html(tl_sub),
            sanitise_string_html(nl_sub),
            sanitise_string_html(sentence_audio_field_anki),
            sanitise_string_html(word_audio_field_anki),
            definition,
            word_frequency,
        ]

        # Create an Anki note
        note = create_note(model, note_fields)
        note_cards.append(note)

        if file_exists(sentence_audio_path):
            media_files.append(sentence_audio_path)

        # Purposefully not file exists, word_audio_path returns None if it can't find it
        if word_audio_path:
            media_files.append(word_audio_path)

        i += 1

    print("Create Anki: Compiling deck")

    # Create deck and add notes
    deck = create_deck(
        deck_id=generate_anki_id(),
        deck_name=deck_name,
        note_cards=note_cards,
    )

    # Package deck and media files
    package = create_package(deck=deck, media_files=media_files)

    # Write to file
    write_package(file_path=deck_output_path, package=package)

    print("Create Anki: Complete")


def frequency_analysis(
    df_input: pd.DataFrame,
    target_language_name: str,
    target_language_abbreviation: str,
    wiki_freq_spreadsheet_path: str,
    output_directory: str,
    game_name: str,
    exclude_list: list,
    max_cards: int,
    lemmatize_words: bool,
) -> pd.DataFrame:

    print("Frequency analysis: loading language model")
    lemma = LemonTizer(language=target_language_abbreviation, model_size="lg")
    lemma.set_lemma_settings(filter_out_non_alpha=True,
            filter_out_common=True,
            convert_input_to_lower=True,
            convert_output_to_lower=True,
            return_just_first_word_of_lemma=True)

    print("Frequency analysis: Counting words (may take a while)")

    df_freq_table = pd.DataFrame(columns=["word", "example", "frequency"])
    total_size = len(df_input)
    i = 0
    for index, row in df_input.iterrows():
        line = row["target_language"]

        word_list = lemma.lemmatize_sentence(input_str=line)

        for word_dict in word_list:
            for word, word_lemma in word_dict.items():

                # Word key is the one that will be processed in the frequency list
                # Word example is the one that we will look up in the game files
                # If we are lemmatising, set the word key to the lemma
                word_key = word
                word_example = word

                if lemmatize_words:
                    word_key = word_lemma

                if word_key in df_freq_table["word"].values:
                    df_freq_table.loc[df_freq_table["word"] == word_key, "frequency"] += 1
                else:
                    new_row = pd.DataFrame(
                        [{"word": word_key, "example": word_example, "frequency": 1}]
                    )
                    df_freq_table = pd.concat([df_freq_table, new_row], ignore_index=True)

        i += 1
        if i % 1000 == 0:
            print(
                f"Frequency analysis counting words, i={i}, {(100*(i/total_size)):.2f}%"
            )

    print("Frequency analysis: Pruning words")
    df_freq_table = df_freq_table.sort_values(by=["frequency"], ascending=False)

    # Remove lines that are either the in top 1000 of the general language (including lemmatisations) or have been set as excluded (e.g. proper nouns)
    df_wiki_freq = pd.read_excel(wiki_freq_spreadsheet_path)
    df_freq_table = df_freq_table[~df_freq_table["word"].isin(df_wiki_freq["word"])]
    df_freq_table = df_freq_table[
        ~df_freq_table["word"].isin(df_wiki_freq["lemma forms"])
    ]
    df_freq_table = df_freq_table[~df_freq_table["word"].isin(exclude_list)]

    # Update to only process the top x from the game and add extra columns
    df_freq_table = df_freq_table.head(max_cards)

    # TODO: This search is no longer necessary, merge into previous bit of code
    print(
        "Frequency analysis: Getting example sentences from the game (may take a while)"
    )

    # Add in extra columns
    df_freq_table = df_freq_table.assign(
        category=" ",
        chapter=" ",
        scene=" ",
        line=" ",
        speaker=" ",
        target_language=" ",
        native_language=" ",
    )

    # Grab the examples for each word
    for index, row in df_freq_table.iterrows():

        line = df_input[
            df_input["target_language"].apply(
                lambda x: full_word_match(x, row["example"])
            )
        ].head(1)

        df_freq_table.at[index, "category"] = line["category"].values
        df_freq_table.at[index, "chapter"] = line["chapter"].values
        df_freq_table.at[index, "scene"] = line["scene"].values
        df_freq_table.at[index, "line"] = line["line"].values
        df_freq_table.at[index, "speaker"] = line["speaker"].values
        df_freq_table.at[index, "target_language"] = line["target_language"].values
        df_freq_table.at[index, "native_language"] = line["native_language"].values

    print("Frequency analysis: Exporting")
    output_spreadsheet = os.path.join(
        output_directory, f"{game_name}_{target_language_name}_Frequency_analysis.xlsx"
    )
    df_freq_table.to_excel(output_spreadsheet, index=False)

    return df_freq_table


def full_word_match(target: str, word: str) -> bool:
    pattern = r"\b" + re.escape(word) + r"\b"

    output = bool(re.search(pattern, target, re.IGNORECASE))

    return output


def remove_punctuation(input_string: str) -> str:
    # Only allow letters/numbers (\w), hyphens (-), apostrophes(')
    # Probably doesn't work for languages that don't use the latin alphabet
    pattern = r"[^\w'-]"

    output_string = re.sub(pattern, "", input_string)
    output_string = output_string.lower()

    return output_string


def format_audio_field(filename: str) -> str:
    """Note to self. You cannot specify audio/sound.mp3 as Anki has a flat file structure.
    All audio files must therefore have unique names
    """

    output_string = f"[sound:{filename}]"

    return output_string


def get_audio_filepath(
    output_folder: str, chapter: str, scene: str, line: str, target_language_name: str
) -> str:

    audio_path = os.path.join(
        output_folder,
        "audio",
        chapter,
        scene,
        target_language_name.lower(),
        line + ".mp3",
    )

    return audio_path


def create_note(model: genanki.Model, fields: list) -> genanki.Note:
    """
    Note to self. No longer sanitising inputs as it prevents html from dictionary from working. Doing it on an individual basis instead.
    """
    note = genanki.Note(model=model, fields=fields)
    return note


def create_model(
    model_id: int, model_name: str, fields: list, template: list, css: str = ""
) -> genanki.Model:

    model = genanki.Model(
        model_id=model_id, name=model_name, fields=fields, templates=template, css=css
    )

    return model


def create_deck(deck_id: int, deck_name: str, note_cards: list) -> genanki.Deck:
    deck = genanki.Deck(deck_id=deck_id, name=deck_name)

    if len(note_cards) > 0:
        for note in note_cards:
            deck.add_note(note)

    return deck


def create_package(deck: genanki.Deck, media_files: list) -> None:
    package = genanki.Package(deck)

    if len(media_files) > 0:
        package.media_files = media_files

    return package


def write_package(file_path: str, package: genanki.Package) -> None:
    package.write_to_file(file_path)


def sanitise_string_html(input_string: str) -> str:
    if type(input_string) == str:
        output_string = html.escape(input_string)
        return output_string
    else:
        return ""


def generate_anki_id() -> int:
    model_id = random.randrange(1 << 30, 1 << 31)

    return model_id


def read_file_to_string(file_path: str) -> str:
    output = ""

    with open(file_path, "r", encoding="utf-8") as file:
        output = file.read()

    return output


def find_file(directory: str, filename: str) -> str:
    for root, _, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def load_json(file_path: str) -> list:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def find_definition(entries: list, search_term: str) -> str:

    if search_term:
        search_term = search_term.lower()

        left = 0
        right = len(entries) - 1

        while left <= right:
            mid = (left + right) // 2
            mid_term = entries[mid]["term"]

            if mid_term == search_term:
                return entries[mid]["definition"]
            elif mid_term < search_term:
                left = mid + 1
            else:
                right = mid - 1

        return ""

    return ""


def file_exists(file_path):
    return os.path.exists(file_path)


if __name__ == "__main__":
    main()
