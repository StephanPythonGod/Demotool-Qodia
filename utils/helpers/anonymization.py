import os
import re
from typing import Any, Dict, List

from flair.data import Sentence
from flair.models import SequenceTagger

from utils.helpers.logger import logger

ENTITIES = [
    "LOCATION",
    "PERSON",
    "ORGANIZATION",
    "DATE_TIME",
    "GENDER_WORD",
    "ID_NUMBER",
]

PRESIDIO_EQUIVALENCES = {
    "PER": "PERSON",
    "LOC": "LOCATION",
    "ORG": "ORGANIZATION",
    "DATE_TIME": "DATE_TIME",
    "GENDER_WORD": "GENDER_WORD",
    "ID_NUMBER": "ID_NUMBER",
}

CHECK_LABEL_GROUPS = [
    ({"LOCATION"}, {"LOC", "LOCATION"}),
    ({"PERSON"}, {"PER", "PERSON"}),
    ({"ORGANIZATION"}, {"ORG"}),
]

MODEL_LANGUAGES = {
    "de": "flair/ner-german-large",
}
MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../models")
MODEL_FILE = os.path.join(MODELS_DIR, "flair-ner-german-large.pt")

DEFAULT_EXPLANATION = "Identified as {} by Flair's Named Entity Recognition"

DATE_PATTERNS = [
    r"\b(?:\d{1,2}\.){1,2}\d{2,4}\b",  # Matches 12.04.2020, 12.04., 12.2020
    r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # Matches 12-04-2020, 12/04/20
    r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",  # Matches 2020-04-12
]

GENDER_WORDS = [
    "frau",
    "frauen",
    "frauens",
    "frau",
    "frauen",
    "frauen",
    "mann",
    "männer",
    "mannes",
    "männern",
    "männer",
    "mann",
    "herr",
    "herren",
    "herrn",
    "herren",
    "herren",
    "dame",
    "damen",
    "dames",
    "dame",
    "damen",
    "damen",
    "fräulein",
    "fräuleins",
    "fräulein",
    "mädchen",
    "mädchens",
    "mädchen",
    "mädchen",
    "junge",
    "jungen",
    "jungens",
    "junge",
    "jugendlicher",
    "jugendliche",
    "jugendlichen",
    "jugendlichen",
    "person",
    "personen",
    "person",
    "persons",
]


def download_model_if_needed():
    """Download the Hugging Face NER model if it does not exist locally."""
    if not os.path.exists(MODEL_FILE):
        logger.info("Downloading Hugging Face model...")
        os.makedirs(MODELS_DIR, exist_ok=True)
        model = SequenceTagger.load(MODEL_LANGUAGES["de"])  # Download the model
        model.save(MODEL_FILE)  # Save it locally
    else:
        logger.info("Model already exists locally.")


def load_model():
    """Load the Hugging Face NER model from the local file."""
    logger.info("Loading the local Hugging Face model...")
    if os.path.exists(MODEL_FILE):
        logger.info("Loading the local Hugging Face model...")
        model = SequenceTagger.load(MODEL_FILE)  # Load the model from local file
    else:
        logger.info("Model not found locally, downloading...")
        download_model_if_needed()
        model = load_model()
    return model


def _anonymize_continuous_numbers(
    text: str, detected_entities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Anonymize continuous numbers of length 5 or more (e.g., IDs) in the text.

    Args:
        text (str): The input text to process.
        detected_entities (List[Dict[str, Any]]): The list to store detected entities.

    Returns:
        List[Dict[str, Any]]: Updated list of detected entities.
    """
    # Regex to match continuous digits with length of 5 or more
    number_pattern = re.compile(r"\b\d{5,}\b")

    # Find all matches in the text
    for match in number_pattern.finditer(text):
        # Add the detected number to the list of detected entities
        detected_entities.append(
            {
                "original_word": match.group(0),
                "entity_type": "ID_NUMBER",
                "start": match.start(),
                "end": match.end(),
                "score": 1.0,  # High confidence as it's an exact match for the pattern
            }
        )

    # Return updated detected_entities
    return detected_entities


def _anonymize_gender_words(text: str, detected_entities: List[Dict[str, Any]]) -> str:
    words = []
    index = 0  # To track the position of the next word
    # Split the text while keeping track of the index of each word
    for word in text.split():
        start_idx = text.index(
            word, index
        )  # Find the word starting at the current index
        words.append((word, start_idx))
        index = start_idx + len(word)  # Move index to the end of the word

    # Iterate over the words and check if they are gender-related words
    for word, start_idx in words:
        # Normalize the word to lowercase for matching and strip punctuation
        normalized_word = word.lower().strip(",.!?;:")
        if normalized_word in GENDER_WORDS:
            # Add the detected gender word to the list of detected entities
            detected_entities.append(
                {
                    "original_word": word,
                    "entity_type": "GENDER_WORD",
                    "start": start_idx,
                    "end": start_idx + len(word),
                    "score": 1.0,  # High confidence for exact match
                }
            )

    # Return updated detected_entities, no need to modify the text here
    return detected_entities


def anonymize_text_german(
    text: str, use_spacy: bool = True, use_flair: bool = True, threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Anonymize German text using NER models (Flair, SpaCy, or both).

    Args:
        text (str): Text to anonymize.
        use_spacy (bool): Use SpaCy for NER (default: True).
        use_flair (bool): Use Flair for NER (default: True).
        threshold (float): Confidence threshold for entity detection (default: 0.8).

    Returns:
        Dict[str, Any]: Dictionary containing anonymized text and detected entities.
    """
    detected_entities = []

    # Identify dates using regular expressions
    for pattern in DATE_PATTERNS:
        for match in re.finditer(pattern, text):
            detected_entities.append(
                {
                    "original_word": match.group(0),
                    "entity_type": "DATE_TIME",
                    "start": match.start(),
                    "end": match.end(),
                    "score": 1.0,  # Assign a high confidence for regex matches
                }
            )

    # Apply gender-word anonymization
    detected_entities = _anonymize_gender_words(
        text, detected_entities=detected_entities
    )

    # Apply continuous number anonymization
    detected_entities = _anonymize_continuous_numbers(
        text, detected_entities=detected_entities
    )

    if use_flair and not use_spacy:
        return _anonymize_flair_only(text, threshold, detected_entities)
    else:
        raise NotImplementedError("SpaCy NER is not implemented.")


def _anonymize_flair_only(
    text: str, threshold: float, detected_entities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Anonymize text using only Flair NER model.

    Args:
        text (str): Text to anonymize.
        threshold (float): Confidence threshold for entity detection.
        detected_entities (List[Dict[str, Any]]): List of already detected entities.

    Returns:
        Dict[str, Any]: Dictionary containing anonymized text and detected entities.
    """
    logger.info("Anonymizing text using Flair NER model")
    # tagger = SequenceTagger.load("flair/ner-german-large")
    tagger = load_model()
    sentence = Sentence(text)
    tagger.predict(sentence)

    # Add NER detected entities from Flair
    flair_entities = [
        {
            "original_word": entity.text,
            "entity_type": entity.get_label("ner").value,
            "start": entity.start_position,
            "end": entity.end_position,
            "score": entity.score,
        }
        for entity in sentence.get_spans("ner")
    ]

    detected_entities.extend(flair_entities)

    # Sort entities by start position in descending order
    detected_entities.sort(key=lambda x: x["start"], reverse=True)

    # Replace entities with placeholders in reverse order
    anonymized_text = text
    for entity in detected_entities:
        presidio_entity_type = PRESIDIO_EQUIVALENCES.get(entity["entity_type"])
        if presidio_entity_type in ENTITIES and entity["score"] > threshold:
            anonymized_text = (
                anonymized_text[: entity["start"]]
                + f"<{presidio_entity_type}>"
                + anonymized_text[entity["end"] :]
            )

    # Filter detected entities by score threshold and ENTITIES
    detected_entities = [
        {
            **entity,
            "entity_type": PRESIDIO_EQUIVALENCES.get(
                entity["entity_type"], entity["entity_type"]
            ),
        }
        for entity in detected_entities
        if entity["score"] > threshold
        and PRESIDIO_EQUIVALENCES.get(entity["entity_type"]) in ENTITIES
    ]

    logger.info(f"Anonymization complete. Detected {len(detected_entities)} entities.")
    return {
        "anonymized_text": anonymized_text,
        "detected_entities": detected_entities,
    }


def anonymize_text(text: str) -> Dict[str, Any]:
    """
    Anonymize the extracted text locally using Flair NER.

    Args:
        text (str): Text to anonymize.

    Returns:
        Dict[str, Any]: Dictionary containing anonymized text and detected entities.
    """
    logger.info("Starting text anonymization ...")
    anonymize_result = anonymize_text_german(text, use_spacy=False, use_flair=True)
    logger.info("Text anonymization completed")
    return anonymize_result
