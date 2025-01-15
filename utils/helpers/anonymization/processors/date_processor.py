import re
from typing import Any, Dict, List

from ..constants import DATE_PATTERNS, GERMAN_MONTHS, GERMAN_WEEKDAYS
from .base import BaseProcessor


class DateProcessor(BaseProcessor):
    """Processor for detecting and anonymizing dates."""

    def _is_valid_date_part(self, text: str) -> bool:
        """Check if a string could be part of a date."""
        text = text.lower().strip(",.!?;: ")

        if text in GERMAN_WEEKDAYS or text in GERMAN_MONTHS:
            return True

        text = text.replace("O", "0").replace("o", "0")

        if text.replace(".", "").isdigit():
            num = int(text.replace(".", ""))
            return (
                (1 <= num <= 31)
                or (1 <= num <= 12)
                or (20 <= num <= 99)
                or (1900 <= num <= 2100)
            )

        return False

    def _detect_split_dates(self, text: str) -> List[Dict[str, Any]]:
        """Detect dates that are split across multiple words."""
        words = text.split()
        detected = []
        i = 0

        while i < len(words):
            if self._is_valid_date_part(words[i]):
                date_parts = [words[i]]
                start_pos = text.find(
                    words[i],
                    0 if i == 0 else text.find(words[i - 1]) + len(words[i - 1]),
                )

                for j in range(1, min(4, len(words) - i)):
                    if self._is_valid_date_part(words[i + j]):
                        date_parts.append(words[i + j])
                    elif len(date_parts) < 2:
                        break

                if len(date_parts) >= 2:
                    combined = " ".join(date_parts)
                    end_pos = start_pos + len(combined)

                    has_number = any(
                        part.replace(".", "").replace("O", "0").isdigit()
                        for part in date_parts
                    )
                    has_month_or_weekday = any(
                        part.lower().strip(",.!?;: ") in GERMAN_MONTHS
                        or part.lower().strip(",.!?;: ") in GERMAN_WEEKDAYS
                        for part in date_parts
                    )

                    if has_number and (has_month_or_weekday or len(date_parts) >= 3):
                        detected.append(
                            {
                                "original_word": combined,
                                "entity_type": "DATE_TIME",
                                "start": start_pos,
                                "end": end_pos,
                                "score": 1.0,
                            }
                        )
                        i += len(date_parts) - 1
            i += 1

        return detected

    def process(
        self, text: str, detected_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process the text to detect dates."""
        # Apply pattern matching for regular dates
        for pattern in DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                detected_entities.append(
                    {
                        "original_word": match.group(0),
                        "entity_type": "DATE_TIME",
                        "start": match.start(),
                        "end": match.end(),
                        "score": 1.0,
                    }
                )

        # Detect split dates
        split_dates = self._detect_split_dates(text)
        detected_entities.extend(split_dates)

        return detected_entities
