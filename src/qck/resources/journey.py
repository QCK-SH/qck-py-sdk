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
            "link_id": "550e8400-e29b-41d4-a716-446655440000",
            "visitor_id": "user-456",
            "session_id": "sess-789",
            "event_type": "page_view",
            "page_url": "/pricing",
        },
    ]})

    # Get journey summary for a link
    summary = client.journey.get_summary("550e8400-e29b-41d4-a716-446655440000", {"period": "30d"})
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        FunnelParams,
        FunnelResult,
        IngestEventsParams,
        JourneyEventsPage,
        JourneyLinkSummary,
        JourneyQueryParams,
        JourneySessionsPage,
        ListJourneyEventsParams,
        ListJourneySessionsParams,
    )


class JourneyResource:
    """Ingest journey events and query link-level journey analytics.

    Access via ``client.journey``. Works with any platform — websites,
    mobile apps, and server-side.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        self._client = client

    def ingest(self, params: "IngestEventsParams") -> None:
        """Ingest a batch of journey events.

        Events are processed asynchronously by the QCK platform.
        Each call generates a unique idempotency key to prevent
        duplicate processing on retries.

        Example:
            >>> client.journey.ingest({"events": [
            ...     {
            ...         "link_id": "550e8400-e29b-41d4-a716-446655440000",
            ...         "visitor_id": "user-456",
            ...         "session_id": "sess-789",
            ...         "event_type": "page_view",
            ...         "page_url": "/pricing",
            ...     },
            ... ]})
        """
        import uuid

        batch_id = str(uuid.uuid4())
        self._client.post(
            "/journey/events",
            dict(params),
            headers={"X-Idempotency-Key": batch_id},
        )

    def get_summary(
        self,
        link_id: str,
        params: Optional["JourneyQueryParams"] = None,
    ) -> "JourneyLinkSummary":
        """Get a journey summary for a specific link.

        Args:
            link_id: The link's UUID.
            params: Optional period filter.

        Returns:
            A summary with visitor/session counts, average session
            duration, and top pages/events.
        """
        return self._client.get(
            f"/journey/links/{link_id}/summary",
            params=dict(params) if params else None,
        )

    def get_funnel(self, link_id: str, params: "FunnelParams") -> "FunnelResult":
        """Run a funnel analysis for a specific link.

        Args:
            link_id: The link's UUID.
            params: Funnel configuration with ordered step names and
                an optional period filter.

        Example:
            >>> funnel = client.journey.get_funnel("abc123", {
            ...     "steps": ["page_view", "signup", "purchase"],
            ...     "period": "30d",
            ... })
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
    ) -> "JourneySessionsPage":
        """List visitor sessions for a specific link.

        Args:
            link_id: The link's UUID.
            params: Pagination, visitor filter, and period options.

        Returns:
            ``{"sessions": [...], "total": int, "page": int, "limit": int}``.

        Example:
            >>> page = client.journey.list_sessions("link-uuid", {"limit": 10})
            >>> for session in page["sessions"]:
            ...     print(session["visitor_id"], session["event_count"])
        """
        return self._client.get(
            f"/journey/links/{link_id}/sessions",
            params=dict(params) if params else None,
        )

    def list_events(
        self,
        link_id: str,
        params: Optional["ListJourneyEventsParams"] = None,
    ) -> "JourneyEventsPage":
        """List journey events for a specific link.

        Args:
            link_id: The link's UUID.
            params: Pagination, event type filter, and period options.

        Returns:
            ``{"events": [...], "total": int, "page": int, "limit": int}``.

        Example:
            >>> page = client.journey.list_events("link-uuid", {"event_type": "custom"})
            >>> for event in page["events"]:
            ...     print(event["event_type"], event["page_url"])
        """
        return self._client.get(
            f"/journey/links/{link_id}/events",
            params=dict(params) if params else None,
        )
