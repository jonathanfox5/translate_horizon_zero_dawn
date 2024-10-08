"""LemonTizer is a class that wraps the spacy library to build a lemmatizer for language 
learning applications.

For class constructor:
    language: Lower case two letter code matching language codes in https://spacy.io/models
    model_size: Lower case two letter code matching sm, md, lg, etc. 
        in https://spacy.io/models

Attributes:
    __init__: Relevant spacy model ("trained pipeline") is downloaded and loaded upon 
        class instanciation.
    set_lemma_settings: To configure parameters for lemmatization
    lematize_sentence: This is the main method for processing text
    
External module requirements:
    spacy
"""

import re

import spacy
from spacy.cli.download import get_compatibility


class LemonTizer:
    """LemonTizer is a class that wraps the spacy library to build a lemmatizer for language 
    learning applications.

    For class constructor:
        language: Lower case two letter code matching language codes in https://spacy.io/models
        model_size: Lower case two letter code matching sm, md, lg, etc. 
            in https://spacy.io/models

    Attributes:
        __init__: Relevant spacy model ("trained pipeline") is downloaded and loaded upon 
            class instanciation.
        set_lemma_settings: To configure parameters for lemmatization
        lematize_sentence: This is the main method for processing text

    External module requirements:
        spacy
    """

    _nlp: spacy.language.Language
    _model_name: str
    _filter_out_non_alpha: bool
    _filter_out_common: bool
    _convert_input_to_lower: bool
    _convert_output_to_lower: bool
    _return_just_first_word_of_lemma: bool

    def __init__(self, language: str = "en", model_size: str = "lg") -> None:
        self.init_model(language=language, model_size=model_size)

    def init_model(self, language: str, model_size: str) -> None:
        """Loads model based upon specified language and model size.
        If model hasn't been downloaded, it will download it prior to the loading step.
        Also loads default settings for lemmatization.

        Args:
            language: Lower case two letter code matching language codes in https://spacy.io/models
            model_size: Lower case two letter code matching sm, md, lg, etc. 
                in https://spacy.io/models
        """

        # Set default settings
        self.set_lemma_settings()

        # Get model name
        model_name = self.find_model_name(language=language, model_size=model_size)

        # Load model, downloading it first if necessary
        if self.is_model_installed(model_name):
            self._load_model(model_name=model_name)
        else:
            self.download_model(model_name=model_name)
            self._load_model(model_name=model_name)

    def set_lemma_settings(self, filter_out_non_alpha: bool = False,
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
        self._filter_out_non_alpha = filter_out_non_alpha
        self._filter_out_common = filter_out_common
        self._convert_input_to_lower = convert_input_to_lower
        self._convert_output_to_lower = convert_output_to_lower
        self._return_just_first_word_of_lemma = return_just_first_word_of_lemma

    def lemmatize_sentence(
        self,
        input_str: str,
    ) -> list[dict[str, str]]:
        """Lemmatizes a sentence (can also be a word, paragraph, etc.)
        Returns:
            Lists of dictionaries which has the original token as the key (str) and lemmatized 
            token as the value (str)

        Args:
            input_str: String containing the data to be lemmatized
        """

        # Pre-process input. Converting to lower can provide better performance with some languages
        if self._convert_input_to_lower:
            input_str = input_str.lower()

        # Process the input string with spacy
        doc = self._nlp(text=input_str)

        # Get the lemmas for each token
        word_list: list[dict[str, str]] = []
        for token in doc:

            # Skip word, depending on settings and properties of the token
            is_not_word = (not token.is_alpha) and self._filter_out_non_alpha
            is_common = token.is_stop and self._filter_out_common
            skip_word = is_not_word or is_common

            if skip_word:
                continue

            # Get lemma for current token and post-process
            lemma = token.lemma_

            if self._return_just_first_word_of_lemma:
                lemma = lemma.split()[0]

            if self._convert_output_to_lower:
                lemma = lemma.lower()

            # Output dictionary is orginal token: lemma
            word_dict = {token.text: lemma}
            word_list.append(word_dict)

        return word_list

    def find_model_name(self, language: str, model_size: str) -> str:
        """Looks up models compatible with the installed version of spacy, based upon language code
        and model size.

        Returns:
            spacy model name (str)
        Args:
            language: Lower case two letter code matching language codes in https://spacy.io/models
            model_size: Lower case two letter code matching sm, md, lg, etc. 
                in https://spacy.io/models
        """

        # Pre-process search terms and build regex object
        language = language.lower()
        model_size = model_size.lower()
        regex = re.compile(f"{language}.*{model_size}")

        # Get list of available models and see if our input is in it
        available_models = self.get_available_models()
        matched_models = list(filter(regex.match, available_models))

        # Return first available model if models have been returned
        if len(matched_models) > 0:
            output = matched_models[0]

            return output

        # Otherwise, there is an error
        # Work out if the language is supported in order to raise the correct error messages
        regex = re.compile(f"^{language}")
        matched_models = list(filter(regex.match, available_models))

        if len(matched_models) > 0:
            error_text = (
                "Model not found for language and model size combination. Both language and"
                "model size should be lower case 2 letter codes" 
                "Supported models: https://spacy.io/models",
            )

        else:
            error_text = (
                f"No models found for language {language}. Languages should be a lower case 2"
                "letter code. Supported languages: https://spacy.io/models",
            )

        raise ValueError(error_text, language, model_size)


    def download_model(self, model_name: str) -> None:
        """Downloads spacy model ("trained pipeline") to local storage
        Args:
            model_name: should match a model in the spacy documentation, 
            see https://spacy.io/models

        Use the method is_model_installed() if you need to check if model has already been 
        downloaded.

        Use the method find_model_name() to get available models based upon language and model size
        """
        spacy.cli.download(model_name)


    def get_available_models(self) -> list[str]:
        """ Gets the list of available pre-trained models for the installed version of spacy
        Returns: 
            List of strings with the names of spacy trained models
        """
        models = get_compatibility().keys()

        return models

    def is_model_installed(self, model_name: str) -> bool:
        """
        Returns:
            True if model is found in local storage, otherwise False
        """
        result = spacy.util.is_package(model_name)

        return result

    def _load_model(self, model_name: str) -> None:
        """ Sets self._model_name and load the model from file into a spacy language object
        Args:
            model_name: should match a model in the spacy documentation, 
            see https://spacy.io/models
        """
        self._model_name = model_name
        self._nlp = spacy.load(name=model_name)

    @property
    def get_current_model_name(self) -> str:
        """
        Returns:
            Name of currently loaded model as a str
        """
        return self._model_name

    @property
    def get_spacy_object(self) -> spacy.language.Language:
        """
        Returns:
            Returns the spacy Language object aka "model" for external processing
        """
        return self._nlp
