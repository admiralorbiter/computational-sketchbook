"""Abstract base collector interface.

All platform collectors implement this interface. The design is deliberately
boring — each method does exactly one thing, returns structured data, and
logs its provenance. The AI harness decides *what* to search; these tools
decide *how* to search and *exactly what was returned*.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from observatory.models import Artifact, Platform


@dataclass
class CollectorCapabilities:
    """Declares what operations a collector supports."""

    can_search: bool = False
    can_fetch: bool = False
    can_fetch_thread: bool = False
    can_stream: bool = False
    can_snapshot_engagement: bool = False
    supported_search_params: list[str] = field(default_factory=list)
    max_results_per_query: int = 100
    requires_auth: bool = False
    rate_limit_info: str = ""


class BaseCollector(ABC):
    """Abstract base class for platform collectors.

    Subclasses must implement the platform-specific methods and declare
    their capabilities. Raw API responses should be preserved for provenance;
    normalized artifacts are returned for the corpus.
    """

    @property
    @abstractmethod
    def platform(self) -> Platform:
        """The platform this collector targets."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Collector version string for provenance tracking."""
        ...

    @abstractmethod
    def capabilities(self) -> CollectorCapabilities:
        """Declare what this collector can do."""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        *,
        limit: int = 50,
        since: str | None = None,
        until: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> tuple[list[Artifact], str | None, list[dict[str, Any]]]:
        """Search the platform for content matching a query.

        Args:
            query: Search query string (platform-specific syntax allowed).
            limit: Maximum number of results to return.
            since: ISO-8601 datetime string for lower time bound.
            until: ISO-8601 datetime string for upper time bound.
            cursor: Pagination cursor from a previous search.
            **kwargs: Platform-specific parameters.

        Returns:
            A tuple of:
            - List of normalized Artifact objects.
            - Next pagination cursor (None if no more results).
            - List of raw API response records (for provenance storage).
        """
        ...

    @abstractmethod
    async def fetch(self, native_id: str) -> tuple[Artifact | None, dict[str, Any] | None]:
        """Fetch a single item by its platform-native identifier.

        Args:
            native_id: The platform's native ID for the content.

        Returns:
            A tuple of the normalized Artifact and raw API response,
            or (None, None) if not found.
        """
        ...

    async def fetch_thread(self, native_id: str) -> tuple[list[Artifact], list[dict[str, Any]]]:
        """Fetch an entire thread/conversation starting from a post.

        Default implementation returns just the single post.
        Override for platforms with native thread support.

        Args:
            native_id: The platform's native ID for the root post.

        Returns:
            A tuple of normalized Artifacts and raw API responses.
        """
        artifact, raw = await self.fetch(native_id)
        if artifact and raw:
            return [artifact], [raw]
        return [], []
