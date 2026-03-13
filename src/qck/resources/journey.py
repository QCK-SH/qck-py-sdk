"""Track and query visitor journeys through the QCK API.

Provides the :class:`JourneyResource` class for ingesting visitor
journey events and querying link-level journey analytics including
summaries, funnel analysis, session listings, and event listings.

Example::

    from qck import QCK

    client = QCK(api_key="qck_...")

    # Ingest journey events
    client.journey.ingest({"events": [
        {
            "link_id": "lnk_abc123",
            "visitor_id": "vis_xyz",
            "session_id": "sess_456",
            "event_type": "page_view",
            "page_url": "https://example.com/landing",
        },
    ]})

    # Get journey summary for a link
    summary = client.journey.get_summary("lnk_abc123", {"period": "30d"})
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        FunnelParams,
        FunnelResult,
        IngestEventsParams,
        JourneyLinkSummary,
        JourneyQueryParams,
        ListJourneyEventsParams,
        ListJourneySessionsParams,
        PaginatedResponse,
    )


class JourneyResource:
    """Ingest journey events and query link-level journey analytics.

    Access via ``client.journey``. Provides methods to send visitor
    behaviour events to the QCK platform and to retrieve analytics
    about how visitors interact after clicking a link.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        """Initialise the journey resource.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def ingest(self, params: "IngestEventsParams") -> None:
        """Ingest a batch of journey events.

        Events are processed asynchronously by the QCK platform.

        Args:
            params: Contains a list of journey events to ingest.

        Raises:
            ValidationError: If any event fails validation.

        Example:
            >>> client.journey.ingest({"events": [
            ...     {
            ...         "link_id": "lnk_abc123",
            ...         "visitor_id": "vis_xyz",
            ...         "session_id": "sess_456",
            ...         "event_type": "page_view",
            ...         "page_url": "https://example.com",
            ...     },
            ... ]})
        """
        self._client.post("/journey/events", dict(params))

    def get_summary(
        self,
        link_id: str,
        params: Optional["JourneyQueryParams"] = None,
    ) -> "JourneyLinkSummary":
        """Get a journey summary for a specific link.

        Returns aggregate metrics about visitor behaviour after
        clicking this link, including top pages and top events.

        Args:
            link_id: The unique link identifier.
            params: Optional period filter. Pass ``None`` to use
                the API default.

        Returns:
            A summary with visitor/session counts, average session
            duration, and top pages/events.

        Raises:
            NotFoundError: If no link exists with the given ID.

        Example:
            >>> summary = client.journey.get_summary(
            ...     "lnk_abc123", {"period": "30d"}
            ... )
            >>> print(summary["total_visitors"])
        """
        return self._client.get(
            f"/journey/links/{link_id}/summary",
            params=dict(params) if params else None,
        )

    def get_funnel(self, link_id: str, params: "FunnelParams") -> "FunnelResult":
        """Run a funnel analysis for a specific link.

        A funnel tracks how many visitors progress through a defined
        sequence of event steps (e.g. page_view -> signup -> purchase).

        Args:
            link_id: The unique link identifier.
            params: Funnel configuration with ordered step names and
                an optional period filter.

        Returns:
            A funnel result with per-step visitor counts and
            conversion rates.

        Raises:
            NotFoundError: If no link exists with the given ID.

        Example:
            >>> funnel = client.journey.get_funnel("lnk_abc123", {
            ...     "steps": ["page_view", "signup", "purchase"],
            ...     "period": "30d",
            ... })
            >>> for step in funnel["steps"]:
            ...     print(step["step_name"], step["conversion_rate"])
        """
        p: Dict[str, str] = {}
        steps = params.get("steps")
        if steps:
            p["steps"] = ",".join(steps)
        period = params.get("period")
        if period:
            p["period"] = period
        return self._client.get(f"/journey/links/{link_id}/funnel", params=p)

    def list_sessions(
        self,
        link_id: str,
        params: Optional["ListJourneySessionsParams"] = None,
    ) -> "PaginatedResponse":
        """List visitor sessions for a specific link.

        Args:
            link_id: The unique link identifier.
            params: Pagination, visitor filter, and period options.
                Pass ``None`` for defaults.

        Returns:
            A paginated response containing session summaries.

        Raises:
            NotFoundError: If no link exists with the given ID.

        Example:
            >>> sessions = client.journey.list_sessions(
            ...     "lnk_abc123", {"limit": 10}
            ... )
            >>> for s in sessions["data"]:
            ...     print(s["session_id"], s["event_count"])
        """
        return self._client.get(
            f"/journey/links/{link_id}/sessions",
            params=dict(params) if params else None,
        )

    def list_events(
        self,
        link_id: str,
        params: Optional["ListJourneyEventsParams"] = None,
    ) -> "PaginatedResponse":
        """List journey events for a specific link.

        Args:
            link_id: The unique link identifier.
            params: Pagination, event type filter, and period options.
                Pass ``None`` for defaults.

        Returns:
            A paginated response containing journey events.

        Raises:
            NotFoundError: If no link exists with the given ID.

        Example:
            >>> events = client.journey.list_events(
            ...     "lnk_abc123",
            ...     {"event_type": "page_view", "limit": 20},
            ... )
        """
        return self._client.get(
            f"/journey/links/{link_id}/events",
            params=dict(params) if params else None,
        )
