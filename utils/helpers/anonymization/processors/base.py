from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseProcessor(ABC):
    """Base class for all anonymization processors."""

    @abstractmethod
    def process(
        self, text: str, detected_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process the text and update detected entities.

        Args:
            text: The input text to process
            detected_entities: List of currently detected entities

        Returns:
            Updated list of detected entities
        """
        pass
