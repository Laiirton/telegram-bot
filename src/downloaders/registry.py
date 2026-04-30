from typing import Type

from src.downloaders.base import BaseExtractor
from src.utils.url_validator import extract_domain


class ExtractorRegistry:
    """Registry that maps domain patterns to extractor classes."""

    def __init__(self) -> None:
        self._extractors: dict[str, Type[BaseExtractor]] = {}

    def register(self, cls: Type[BaseExtractor]) -> None:
        """Register an extractor class for its domains."""
        for domain in cls.DOMAINS:
            self._extractors[domain] = cls

    def resolve(self, url: str) -> BaseExtractor:
        """Get the appropriate extractor for a URL."""
        domain = extract_domain(url)
        if domain not in self._extractors:
            raise ValueError(f"No extractor registered for domain: {domain}")
        return self._extractors[domain]()
