import re
from typing import Any, Dict, List

from ..constants import FINANCIAL_PATTERNS
from .base import BaseProcessor


class FinancialProcessor(BaseProcessor):
    """Processor for detecting and anonymizing financial IDs and phone numbers."""

    def _is_potential_phone_number(self, text: str) -> bool:
        """Check if a string could be part of a phone number."""
        text = text.replace("O", "0").replace("o", "0")
        cleaned = text.replace("-", "").replace("/", "").replace(" ", "")
        if "." in text:
            return False
        return cleaned.isdigit() and 2 <= len(cleaned) <= 5

    def _detect_consecutive_numbers(self, text: str) -> List[Dict[str, Any]]:
        """Detect potential phone numbers from consecutive number-like groups."""
        words = text.split()
        detected = []
        i = 0

        while i < len(words):
            if self._is_potential_phone_number(words[i]):
                number_parts = [words[i]]
                start_pos = text.find(
                    words[i],
                    0 if i == 0 else text.find(words[i - 1]) + len(words[i - 1]),
                )

                while i + 1 < len(words) and self._is_potential_phone_number(
                    words[i + 1]
                ):
                    number_parts.append(words[i + 1])
                    i += 1

                if len(number_parts) >= 2:
                    combined = " ".join(number_parts)
                    end_pos = start_pos + len(combined)

                    detected.append(
                        {
                            "original_word": combined,
                            "entity_type": "FINANCIAL_ID",
                            "start": start_pos,
                            "end": end_pos,
                            "score": 1.0,
                        }
                    )
            i += 1

        return detected

    def process(
        self, text: str, detected_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process the text to detect financial IDs and phone numbers."""
        # Use regex patterns
        for pattern in FINANCIAL_PATTERNS:
            flags = re.IGNORECASE if not any(c.isupper() for c in pattern) else 0
            for match in re.finditer(pattern, text, flags=flags):
                if any(char.isdigit() or char in "/:.-" for char in match.group(0)):
                    detected_entities.append(
                        {
                            "original_word": match.group(0),
                            "entity_type": "FINANCIAL_ID",
                            "start": match.start(),
                            "end": match.end(),
                            "score": 1.0,
                        }
                    )

        # Detect consecutive number groups
        consecutive_numbers = self._detect_consecutive_numbers(text)
        detected_entities.extend(consecutive_numbers)

        return detected_entities
