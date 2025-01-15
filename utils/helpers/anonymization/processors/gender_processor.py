from typing import Any, Dict, List

from ..constants import GENDER_WORDS
from .base import BaseProcessor


class GenderProcessor(BaseProcessor):
    """Processor for detecting and anonymizing gender-related words."""

    def process(
        self, text: str, detected_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process the text to detect gender words."""
        words = []
        index = 0

        for word in text.split():
            start_idx = text.index(word, index)
            words.append((word, start_idx))
            index = start_idx + len(word)

        for word, start_idx in words:
            normalized_word = word.lower().strip(",.!?;:")
            if normalized_word in GENDER_WORDS:
                detected_entities.append(
                    {
                        "original_word": word,
                        "entity_type": "GENDER_WORD",
                        "start": start_idx,
                        "end": start_idx + len(word),
                        "score": 1.0,
                    }
                )

        return detected_entities
