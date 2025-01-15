from typing import Any, Dict, List

from utils.helpers.logger import logger

from .constants import ENTITIES
from .processors.base import BaseProcessor
from .processors.date_processor import DateProcessor
from .processors.financial_processor import FinancialProcessor
from .processors.gender_processor import GenderProcessor
from .processors.ner_processor import NERProcessor


class Anonymizer:
    """Main class for text anonymization."""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.processors: List[BaseProcessor] = [
            DateProcessor(),
            FinancialProcessor(),
            GenderProcessor(),
            NERProcessor(threshold=threshold),
        ]

    def anonymize(self, text: str) -> Dict[str, Any]:
        """
        Anonymize the text using all processors.

        Args:
            text: Text to anonymize

        Returns:
            Dict containing anonymized text and detected entities
        """
        detected_entities = []

        # Process text with all processors
        for processor in self.processors:
            detected_entities = processor.process(text, detected_entities)

        # Sort entities by start position in descending order
        detected_entities.sort(key=lambda x: x["start"], reverse=True)

        # Replace entities with placeholders in reverse order
        anonymized_text = text
        for entity in detected_entities:
            if entity["entity_type"] in ENTITIES and entity["score"] > self.threshold:
                anonymized_text = (
                    anonymized_text[: entity["start"]]
                    + f"<{entity['entity_type']}>"
                    + anonymized_text[entity["end"] :]
                )

        return {
            "anonymized_text": anonymized_text,
            "detected_entities": detected_entities,
        }


def anonymize_text(text: str) -> Dict[str, Any]:
    """
    Anonymize the extracted text locally using all processors.

    Args:
        text: Text to anonymize

    Returns:
        Dict containing anonymized text and detected entities
    """
    logger.info("Starting text anonymization ...")
    anonymizer = Anonymizer()
    result = anonymizer.anonymize(text)
    logger.info("Text anonymization completed")
    return result


def anonymize_text_german(
    text: str, use_spacy: bool = True, use_flair: bool = True, threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Maintain backward compatibility with the old API.
    """
    if use_spacy:
        raise NotImplementedError("SpaCy NER is not implemented.")
    anonymizer = Anonymizer(threshold=threshold)
    return anonymizer.anonymize(text)


"""
Text anonymization module for German text.

This module provides functionality to anonymize sensitive information in text,
including personal names, locations, organizations, dates, financial IDs,
and gender-specific words.

The module uses various processors including pattern matching and NER to
detect and anonymize sensitive information.
"""
