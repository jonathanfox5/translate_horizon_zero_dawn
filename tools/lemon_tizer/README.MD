# Description

LemonTizer is a class that wraps the [spacy](https://spacy.io) library to build a lemmatizer for language learning applications. It automatically manages the installation and loading of all [languages](https://spacy.io/models) supported by spacy and provides various lemmatizations options.

It is designed so that lemmatization can be enabled for multiple languages with the same amount of effort as enabling it for one, thus making community made scripts more widely accessible.

`lemon_tizer.py` is fully documented to make it easier to make changes.

(for those curious, lemon tizer is a pun on the [Scottish soft drink](https://en.wikipedia.org/wiki/Tizer) which comes in various fruit flavours)

# Quickstart

First, install spacy using pip:

```bash
pip install spacy
```

Example of lemmatizing a single sentence:

```python
# Import class
from lemon_tizer import LemonTizer

# Initialise class
# Language should be a lower case 2 letter code, see "Supported Languages" table for list of abbreviations
# Model size depends on availability of models, see https://spacy.io/models
# Normally, these are "sm", "md", "lg"
# Larger models are more accurate and support more features but require more storage space and may take longer to run
lemma = LemonTizer(language="en", model_size= "lg")

# Lemmatize a test string and print the result
test_string = "I am going to the shops to buy a can of Tizer."
output = lemma.lemmatize_sentence(test_string)
print(output)
```

This would produce the following output:

```python
"""
Output:
[{'I': 'I'},
 {'am': 'be'},
 {'going': 'go'},
 {'to': 'to'},
 {'the': 'the'},
 {'shops': 'shop'},
 {'to': 'to'},
 {'buy': 'buy'},
 {'a': 'a'},
 {'can': 'can'},
 {'of': 'of'},
 {'Tizer': 'Tizer'},
 {'.': '.'}]
"""
```

# Script settings

You can also enable various settings to exclude punctuation, exclude common words, force the input to lower case to change the behaviour, etc. A use case of this would be creating a frequency analysis of calculating the words in a text.

Example:

```python
# Import class
from lemon_tizer import LemonTizer

# Initialise class
lemma = LemonTizer(language="en", model_size= "lg")

# Configure settings
lemma.set_lemma_settings(filter_out_non_alpha=True,
    filter_out_common=True,
    convert_input_to_lower=True,
    convert_output_to_lower=True,
    return_just_first_word_of_lemma=True
)

# Lemmatize a test string and print the result
test_string = "I am going to the shops to buy a can of Tizer."
output = lemma.lemmatize_sentence(test_string)
print(output)
```

This would produce the following output:

```python
"""
Output:
[{'going': 'go'}, {'shops': 'shop'}, {'buy': 'buy'}, {'tizer': 'tizer'}]
"""
```

The options are:

| Boolean Variable                | Explanation                                                                                                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| filter_out_non_alpha            | Will filter out lemmatizations that contain non-alpha characters. Useful for removing punctuation, etc. Note: lemmatizations with an apostrophe will also be filtered if this is set! |
| filter_out_common               | Will filter out common words such as "the, and, she". Useful when doing frequency analysis.                                                                                           |
| convert_input_to_lower          | Forces the input string to lowercase. May be useful to increase accuracy in some languages.                                                                                           |
| convert_output_to_lower         | Forces the lemmatization to be lower case to change the behaviour of the algorithm, particularly in relation to the identification of proper nouns.                                   |
| return_just_first_word_of_lemma | Some lemmatizations will return multiple words for a given input token. Setting this to True will return just the first word.                                                         |

# Advanced Functions

You can call `LemonTizer.get_spacy_object()` to get the underlying spacy object which has been initialised to a given model, should you wish to use functions not exposed by the wrapper.

# Public Functions and Properties

```python

def init_model(language: str, model_size: str) -> None:
    """Loads model based upon specified language and model size.
    If model hasn't been downloaded, it will download it prior to the loading step.
    Also loads default settings for lemmatization.

    Args:
        language: Lower case two letter code matching language codes in https://spacy.io/models
        model_size: Lower case two letter code matching sm, md, lg, etc.
            in https://spacy.io/models
    """

def set_lemma_settings(filter_out_non_alpha: bool = False,
    filter_out_common: bool = False,
    convert_input_to_lower: bool = False,
    convert_output_to_lower: bool = False,
    return_just_first_word_of_lemma: bool = False) -> None:
    """ Sets various settings for lemmatisation
    Args:
        filter_out_non_alpha: (bool) Will filter out lemmatizations that contain non-alpha
            characters. Useful for removing punctuation, etc. Note: lemmatizations with an
            apostrophe will also be filtered if this is set!
        filter_out_common: (bool) Will filter out common words such as "the, and, she". Useful
            when doing frequency analysis.
        convert_input_to_lower: (bool) Forces the input string to lowercase. May be useful to
            increase accuracy in some languages.
        convert_output_to_lower: (bool) Optionally force the lemmatization to be lower case.
        return_just_first_word_of_lemma: (bool) Some lemmatizations will return multiple words
            for a given input token. Setting this to True will return just the first word.
    """

def lemmatize_sentence(input_str: str) -> list[dict[str, str]]:
    """Lemmatizes a sentence (can also be a word, paragraph, etc.)
    Returns:
        Lists of dictionaries which has the original token as the key (str) and lemmatized
        token as the value (str)

    Args:
        input_str: String containing the data to be lemmatized
    """

def find_model_name(language: str, model_size: str) -> str:
    """Looks up models compatible with the installed version of spacy, based upon language code
    and model size.

    Returns:
        spacy model name (str)
    Args:
        language: Lower case two letter code matching language codes in https://spacy.io/models
        model_size: Lower case two letter code matching sm, md, lg, etc.
            in https://spacy.io/models
    """

def download_model(model_name: str) -> None:
    """Downloads spacy model ("trained pipeline") to local storage
    Args:
        model_name: should match a model in the spacy documentation,
        see https://spacy.io/models

    Use the method is_model_installed() if you need to check if model has already been
    downloaded.

    Use the method find_model_name() to get available models based upon language and model size
    """

def get_available_models() -> list[str]:
        """ Gets the list of available pre-trained models for the installed version of spacy
        Returns:
            List of strings with the names of spacy trained models
        """

def is_model_installed(model_name: str) -> bool:
        """
        Returns:
            True if model is found in local storage, otherwise False
        """
@property
def get_current_model_name() -> str:
    """
    Returns:
        Name of currently loaded model as a str
    """

@property
def get_spacy_object() -> spacy.language.Language:
    """
    Returns:
        Returns the spacy Language object aka "model" for external processing
    """
```

# Supported languages

The supported languages are determined by the installed version of spacy, see here: [languages](https://spacy.io/models).

At the time of writing, the following languages are supported:

| Abbreviation | Language Name    |
| ------------ | ---------------- |
| ca           | Catalan          |
| zh           | Chinese          |
| hr           | Croatian         |
| da           | Danish           |
| nl           | Dutch            |
| en           | English          |
| fi           | Finnish          |
| fr           | French           |
| de           | German           |
| el           | Greek            |
| it           | Italian          |
| ja           | Japanese         |
| ko           | Korean           |
| lt           | Lithuanian       |
| mk           | Macedonian       |
| xx           | Multi-language   |
| nb           | Norwegian Bokmål |
| pl           | Polish           |
| pt           | Portuguese       |
| ro           | Romanian         |
| ru           | Russian          |
| sl           | Slovenian        |
| es           | Spanish          |
| sv           | Swedish          |
| uk           | Ukrainian        |

# Acknowledgements

Unless otherwise noted, all materials within this repository are Copyright (C) 2024 Jonathan Fox.
