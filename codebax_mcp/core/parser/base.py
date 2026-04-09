"""Base parser interface."""

from abc import ABC, abstractmethod
from typing import List
from .models import Symbol


class BaseParser(ABC):
    """Abstract base class for all parsers."""

    @abstractmethod
    def parse_file(self, file_path: str) -> List[Symbol]:
        """Parse a file and extract symbols."""
        pass

    @abstractmethod
    def parse_content(self, content: str, file_path: str, language: str) -> List[Symbol]:
        """Parse content string and extract symbols."""
        pass
