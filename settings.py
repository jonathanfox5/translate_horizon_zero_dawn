"""
Set your file locations and languages here.

Game root is the "Packed_DX12" folder within your game installation

Languages can be one of: English, French, Spanish, German, Italian, Dutch, Portuguese, TraditionalChinese, Korean, Russian, Polish, Danish, Finnish, Norwegian, Swedish, Japanese, LatinAmericanSpanish, BrazilianPortuguese, Turkish, Arabic, SimplifiedChinese
Language name needs to be prefixed with "ETextLanguages." e.g. NATIVE_LANG = ETextLanguages.English
Include audio can be True or False. True if you have extracted the data, False if you haven't. Script runs much faster if set to False.
"""

from pydecima.enums import ETextLanguages

GAME_ROOT = r"C:\Program Files (x86)\Steam\steamapps\common\Horizon Zero Dawn"

NATIVE_LANG = ETextLanguages.English
TARGET_LANG = ETextLanguages.Italian

INCLUDE_AUDIO = True


"""
These only need to be set if you want to generate Anki decks
ANKI_MAX_CARDS is the number of cards in the Anki deck. I recommend that you don't go above around 1000, otherwise the script will take a while to run.
Dictionary path is the location of the json dictionary for your language and is used for working out the definition to put on the Anki card
Work audio path is used to read out the word on the front of the card
Anki exclude is a list of specific words that you don't want added to the Anki deck. By default, I've set these to be the proper names within the world e.g. Aloy, Nora, etc. Note that these might be different in languages that aren't Italian!
"""
ANKI_MAX_CARDS = 1000

DICTIONARY_PATH = r"C:\Users\jonat\Dictionaries\Migaku\Vicon_Ita_to_Eng_Dictionary.json"
WORD_AUDIO_PATH = r"C:\Users\jonat\Dictionaries"

ANKI_EXCLUDE = [
    "nora",
    "carja",
    "aloy",
    "banuk",
    "oseram",
    "gaia",
    "ban-ur",
    "elisabet",
    "elisabeth"
    "dervahl",
    "rost",
    "olin",
    "helis",
    "sobeck",
    "nakoa",
    "sylens",
    "un'oseram",
    "jiran",
    "banukai",
    "meridiana",
    "werak",
    "aratak",
    "avad",
    "focus",
    "uhm",
    "ehm",
    "ourea",
]


"""
You shouldn't need to change the following unless you are making changes to the script
"""
UNPACKED_ROOT = r"unpacked_files"
OUTPUT_FOLDER = r"output"
CONVERTER_PATH = r"tools\vgaudio\VGAudioCli.exe"
HTML_TEMPLATE_PATH = r"html_source\template_minimised.html"
SENTENCE_DUMPER_PATH = r"tools\decima-scripts\sentence_dumper"
DECIMA_EXPLORER_PATH = r"tools\decimaexplorer\DecimaExplorer-GUI.exe"
DECIMA_EXPLORER_CLI = r"tools\decimaexplorer\DecimaExplorer.exe"
ANKI_TEMPLATE_DIRECTORY = r"html_source\anki"
GENERAL_1000_WORDS_PATH = r"reference\top1000_words.xlsx"
DECIMA_VERSION = "HZDPC"

"""
You shouldn't need to change the following unless you are making changes to the script
These change the categories for each of the scenes
"""
DEFAULT_CATEGORY = "99 Other"
CHAPTER_IDENTIFIERS = {
    "mq01_papooserider": "00 Intro",
    "mq": "01 Main Quests",
    "tc": "02 Side Quests",
    "tn": "02 Side Quests",
    "ts": "02 Side Quests",
    "dlc1_tb": "03 DLC Quests",
    "aigenerated": "20 NPC Lines",
}
SCENE_IDENTIFIERS = {
    "callouts": "11 Callouts",
    "audiologs": "10 Audiologs",
    "placeholder": "99 Other",
}
