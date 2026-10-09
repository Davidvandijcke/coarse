"""Optional execution services for the review orchestrator."""

from __future__ import annotations

from typing import Protocol


class ReviewRuntime(Protocol):
    """Alternate reasoning transport; the default pipeline remains unchanged."""

    def create_client(self, **kwargs): ...
    def search_literature(self, title, abstract, client, deep_search=False, **kwargs): ...
    def completed_futures(self, futures, **kwargs): ...
