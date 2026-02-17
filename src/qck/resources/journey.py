"""Track and query visitor journeys through the QCK API."""

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
    """Ingest journey events and query link-level journey analytics."""

    def __init__(self, client: "HttpClient") -> None:
        self._client = client

    def ingest(self, params: "IngestEventsParams") -> None:
        self._client.post("/journey/events", dict(params))

    def get_summary(
        self,
        link_id: str,
        params: Optional["JourneyQueryParams"] = None,
    ) -> "JourneyLinkSummary":
        return self._client.get(
            f"/journey/links/{link_id}/summary",
            params=dict(params) if params else None,
        )

    def get_funnel(self, link_id: str, params: "FunnelParams") -> "FunnelResult":
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
        return self._client.get(
            f"/journey/links/{link_id}/sessions",
            params=dict(params) if params else None,
        )

    def list_events(
        self,
        link_id: str,
        params: Optional["ListJourneyEventsParams"] = None,
    ) -> "PaginatedResponse":
        return self._client.get(
            f"/journey/links/{link_id}/events",
            params=dict(params) if params else None,
        )
