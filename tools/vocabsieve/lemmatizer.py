"""
Based upon https://github.com/FreeLanguageTools/vocabsieve/blob/master/vocabsieve/lemmatizer.py
Cut down to remove pymorphy3 and instead use simplemma in all instances
"""

import simplemma
import re
from functools import lru_cache

simplemma_languages = [
    "ast",
    "bg",
    "ca",
    "cs",
    "cy",
    "da",
    "de",
    "el",
    "en",
    "enm",
    "es",
    "et",
    "fa",
    "fi",
    "fr",
    "ga",
    "gd",
    "gl",
    "gv",
    "hbs",
    "hi",
    "hu",
    "hy",
    "id",
    "is",
    "it",
    "ka",
    "la",
    "lb",
    "lt",
    "lv",
    "mk",
    "ms",
    "nb",
    "nl",
    "nn",
    "pl",
    "pt",
    "ro",
    "ru",
    "se",
    "sk",
    "sl",
    "sq",
    "sv",
    "sw",
    "tl",
    "tr",
    "uk",
]


def lem_pre(word: str, language: str) -> str:
    _ = language
    word = re.sub(r'[\?\.!«»”“"…,()\[\]]*', "", word).strip()
    word = re.sub(r"<.*?>", "", word)
    word = re.sub(r"\{.*?\}", "", word)
    return word


def lem_word(word, language, greedy=False):
    return lemmatize(lem_pre(word, language), language, greedy)


@lru_cache(maxsize=500000)
def lemmatize(word: str, language, greedy: bool = False) -> str:
    try:
        if not word:
            return word
        if language in simplemma_languages:
            return simplemma.lemmatize(word, lang=language, greedy=greedy)
        else:
            return word
    except ValueError as e:
        print("encountered ValueError", repr(e))
        return word
    except Exception as e:
        print(repr(e))
        return word
