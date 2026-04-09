"""Study Session Tracker — Note service layer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StudyModels:
    """Business-logic service for Note operations in Study Session Tracker."""

    def __init__(
        self,
        repo: Any,
        events: Optional[Any] = None,
    ) -> None:
        self._repo   = repo
        self._events = events
        logger.debug("StudyModels started")

    def end(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the end workflow for a new Note."""
        if "duration_mins" not in payload:
            raise ValueError("Missing required field: duration_mins")
        record = self._repo.insert(
            payload["duration_mins"], payload.get("focus_score"),
            **{k: v for k, v in payload.items()
              if k not in ("duration_mins", "focus_score")}
        )
        if self._events:
            self._events.emit("note.endd", record)
        return record

    def review(self, rec_id: str, **changes: Any) -> Dict[str, Any]:
        """Apply *changes* to a Note and emit a change event."""
        ok = self._repo.update(rec_id, **changes)
        if not ok:
            raise KeyError(f"Note {rec_id!r} not found")
        updated = self._repo.fetch(rec_id)
        if self._events:
            self._events.emit("note.reviewd", updated)
        return updated

    def start(self, rec_id: str) -> None:
        """Remove a Note and emit a removal event."""
        ok = self._repo.delete(rec_id)
        if not ok:
            raise KeyError(f"Note {rec_id!r} not found")
        if self._events:
            self._events.emit("note.startd", {"id": rec_id})

    def search(
        self,
        duration_mins: Optional[Any] = None,
        status: Optional[str] = None,
        limit:  int = 50,
    ) -> List[Dict[str, Any]]:
        """Search notes by *duration_mins* and/or *status*."""
        filters: Dict[str, Any] = {}
        if duration_mins is not None:
            filters["duration_mins"] = duration_mins
        if status is not None:
            filters["status"] = status
        rows, _ = self._repo.query(filters, limit=limit)
        logger.debug("search notes: %d hits", len(rows))
        return rows

    @property
    def stats(self) -> Dict[str, int]:
        """Quick summary of Note counts by status."""
        result: Dict[str, int] = {}
        for status in ("active", "pending", "closed"):
            _, count = self._repo.query({"status": status}, limit=0)
            result[status] = count
        return result
