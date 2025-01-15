from typing import Any, Dict, List

from flair.data import Sentence

from ..constants import PRESIDIO_EQUIVALENCES, WHITELIST
from ..models import load_model
from .base import BaseProcessor


class NERProcessor(BaseProcessor):
    """Processor for Named Entity Recognition using Flair."""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.model = load_model()

    def process(
        self, text: str, detected_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process the text using Flair NER model."""
        sentence = Sentence(text)
        self.model.predict(sentence)

        # Add NER detected entities from Flair
        for entity in sentence.get_spans("ner"):
            # Skip single-character entities and whitelisted terms
            if (
                len(entity.text.strip()) <= 1
                or entity.text.lower().strip() in WHITELIST
            ):
                continue

            presidio_entity_type = PRESIDIO_EQUIVALENCES.get(
                entity.get_label("ner").value
            )
            if presidio_entity_type and entity.score > self.threshold:
                detected_entities.append(
                    {
                        "original_word": entity.text,
                        "entity_type": presidio_entity_type,
                        "start": entity.start_position,
                        "end": entity.end_position,
                        "score": entity.score,
                    }
                )

        return detected_entities
