import re
from typing import Any, Dict, List, Optional, Set, Tuple

from flair.data import Sentence
from flair.models import SequenceTagger
from presidio_analyzer import (
    AnalysisExplanation,
    AnalyzerEngine,
    EntityRecognizer,
    RecognizerResult,
)
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

ENTITIES = ["LOCATION", "PERSON", "ORGANIZATION", "DATE_TIME"]

PRESIDIO_EQUIVALENCES = {
    "PER": "PERSON",
    "LOC": "LOCATION",
    "ORG": "ORGANIZATION",
    "DATE_TIME": "DATE_TIME",
}

# Supported entities and label groups mapping Flair to Presidio
CHECK_LABEL_GROUPS = [
    ({"LOCATION"}, {"LOC", "LOCATION"}),
    ({"PERSON"}, {"PER", "PERSON"}),
    ({"ORGANIZATION"}, {"ORG"}),
]
MODEL_LANGUAGES = {
    "de": "flair/ner-german-large",
}

DEFAULT_EXPLANATION = "Identified as {} by Flair's Named Entity Recognition"

DATE_PATTERNS = [
    r"\b(?:\d{1,2}\.){1,2}\d{2,4}\b",  # Matches 12.04.2020, 12.04., 12.2020
    r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # Matches 12-04-2020, 12/04/20
    r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",  # Matches 2020-04-12
]


class FlairRecognizer(EntityRecognizer):
    """
    Recognizer that uses a Flair NER model for
    entity recognition in German texts.
    """

    def __init__(
        self,
        supported_language: str = "de",
        supported_entities: Optional[List[str]] = None,
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        model: SequenceTagger = None,
    ):
        self.check_label_groups = (
            check_label_groups if check_label_groups else self.CHECK_LABEL_GROUPS
        )
        supported_entities = supported_entities if supported_entities else self.ENTITIES
        self.model = (
            model
            if model
            else SequenceTagger.load(self.MODEL_LANGUAGES.get(supported_language))
        )

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="Flair Recognizer",
        )

    def load(self) -> None:
        """Load the model, not used. Model is loaded during initialization."""
        pass

    def get_supported_entities(self) -> List[str]:
        """Return supported entities by this model."""
        return self.supported_entities

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: Dict[str, Any] = None
    ) -> List[RecognizerResult]:
        """
        Analyze the text using Flair NER model.

        :param text: Text to analyze.
        :param entities: List of entity types to recognize.
        :param nlp_artifacts: Not used by this recognizer.
        :return: List of Presidio RecognizerResult objects.
        """
        results = []
        sentence = Sentence(text)
        self.model.predict(sentence)

        if not entities:
            entities = self.supported_entities

        for entity in entities:
            if entity not in self.supported_entities:
                continue

            for ent in sentence.get_spans("ner"):
                if not self.__check_label(
                    entity, ent.labels[0].value, self.check_label_groups
                ):
                    continue

                textual_explanation = self.DEFAULT_EXPLANATION.format(
                    ent.labels[0].value
                )
                explanation = self.build_flair_explanation(
                    round(ent.score, 2), textual_explanation
                )
                flair_result = self._convert_to_recognizer_result(ent, explanation)

                results.append(flair_result)

        return results

    def _convert_to_recognizer_result(self, entity, explanation) -> RecognizerResult:
        """
        Convert a Flair entity into a Presidio RecognizerResult.

        :param entity: Detected entity from Flair NER.
        :param explanation: AnalysisExplanation object explaining the detection.
        :return: RecognizerResult object.
        """
        entity_type = self.PRESIDIO_EQUIVALENCES.get(entity.tag, entity.tag)
        flair_score = round(entity.score, 2)

        return RecognizerResult(
            entity_type=entity_type,
            start=entity.start_position,
            end=entity.end_position,
            score=flair_score,
            analysis_explanation=explanation,
        )

    def build_flair_explanation(
        self, original_score: float, explanation: str
    ) -> AnalysisExplanation:
        """
        Create explanation for why this result was detected.

        :param original_score: Score given by this recognizer.
        :param explanation: Explanation string.
        :return: AnalysisExplanation object.
        """
        return AnalysisExplanation(
            recognizer=self.__class__.__name__,
            original_score=original_score,
            textual_explanation=explanation,
        )

    @staticmethod
    def __check_label(
        entity: str, label: str, check_label_groups: Tuple[Set, Set]
    ) -> bool:
        """
        Check if the entity and label are part of the predefined label groups.

        :param entity: Presidio entity type (e.g., PERSON, LOCATION).
        :param label: Flair entity label (e.g., PER, LOC).
        :param check_label_groups: Set of entity-label pairs to check.
        :return: Boolean indicating if label matches the entity.
        """
        return any(
            [entity in egrp and label in lgrp for egrp, lgrp in check_label_groups]
        )


def setup_analyzer(use_spacy: bool = True, use_flair: bool = True) -> AnalyzerEngine:
    """
    Set up the Presidio AnalyzerEngine with optional Flair and SpaCy integration.

    :param use_spacy: Whether to use SpaCy for NER.
    :param use_flair: Whether to use Flair for NER.
    :return: Configured AnalyzerEngine object.
    """
    nlp_engine = None
    if use_spacy:
        spacy_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "de", "model_name": "de_core_news_lg"}],
        }
        provider = NlpEngineProvider(nlp_configuration=spacy_configuration)
        nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages="de")

    if use_flair:
        flair_recognizer = FlairRecognizer()
        analyzer.registry.add_recognizer(flair_recognizer)

    return analyzer


def anonymize_text_german(
    text: str, use_spacy: bool = True, use_flair: bool = True, threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Anonymize German text using NER models (Flair, SpaCy, or both).

    :param text: Text to anonymize.
    :param use_spacy: Use SpaCy for NER.
    :param use_flair: Use Flair for NER.
    :return: Dictionary containing anonymized text and detected entities.
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

    if use_flair and not use_spacy:
        # Flair-only case optimization
        tagger = SequenceTagger.load("flair/ner-german-large")
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
            {**entity, "entity_type": PRESIDIO_EQUIVALENCES.get(entity["entity_type"])}
            for entity in detected_entities
        ]

        detected_entities = [
            entity
            for entity in detected_entities
            if entity["score"] > threshold and entity["entity_type"] in ENTITIES
        ]

        return {
            "anonymized_text": anonymized_text,
            "detected_entities": detected_entities,
        }
    else:
        # Presidio-based anonymization using either SpaCy or Flair
        analyzer = setup_analyzer(use_spacy, use_flair)
        entities_to_anonymize = ENTITIES

        analyzer_results = analyzer.analyze(
            text=text, entities=entities_to_anonymize, language="de"
        )

        anonymizer_engine = AnonymizerEngine()
        anonymized_result = anonymizer_engine.anonymize(
            text=text, analyzer_results=analyzer_results
        )

        presidio_entities = [
            {**entity.to_dict(), "original_word": text[entity.start : entity.end]}
            for entity in analyzer_results
        ]

        detected_entities.extend(presidio_entities)

        return {
            "anonymized_text": anonymized_result.text,
            "detected_entities": detected_entities,
        }


def anonymize_text(text):
    """
    Anonymize the extracted text locally.
    """

    anonymize_result = anonymize_text_german(text, use_spacy=False, use_flair=True)

    return anonymize_result
