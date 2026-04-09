"""Study Session Tracker — Goal service layer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StudyWorker:
    """Business-logic service for Goal operations in Study Session Tracker."""

    def __init__(
        self,
        repo: Any,
        events: Optional[Any] = None,
    ) -> None:
        self._repo   = repo
        self._events = events
        logger.debug("StudyWorker started")

    def start(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the start workflow for a new Goal."""
        if "break_count" not in payload:
            raise ValueError("Missing required field: break_count")
        record = self._repo.insert(
            payload["break_count"], payload.get("subject_id"),
            **{k: v for k, v in payload.items()
              if k not in ("break_count", "subject_id")}
        )
        if self._events:
            self._events.emit("goal.startd", record)
        return record

    def resume(self, rec_id: str, **changes: Any) -> Dict[str, Any]:
        """Apply *changes* to a Goal and emit a change event."""
        ok = self._repo.update(rec_id, **changes)
        if not ok:
            raise KeyError(f"Goal {rec_id!r} not found")
        updated = self._repo.fetch(rec_id)
        if self._events:
            self._events.emit("goal.resumed", updated)
        return updated

    def export(self, rec_id: str) -> None:
        """Remove a Goal and emit a removal event."""
        ok = self._repo.delete(rec_id)
        if not ok:
            raise KeyError(f"Goal {rec_id!r} not found")
        if self._events:
            self._events.emit("goal.exportd", {"id": rec_id})

    def search(
        self,
        break_count: Optional[Any] = None,
        status: Optional[str] = None,
        limit:  int = 50,
    ) -> List[Dict[str, Any]]:
        """Search goals by *break_count* and/or *status*."""
        filters: Dict[str, Any] = {}
        if break_count is not None:
            filters["break_count"] = break_count
        if status is not None:
            filters["status"] = status
        rows, _ = self._repo.query(filters, limit=limit)
        logger.debug("search goals: %d hits", len(rows))
        return rows

    @property
    def stats(self) -> Dict[str, int]:
        """Quick summary of Goal counts by status."""
        result: Dict[str, int] = {}
        for status in ("active", "pending", "closed"):
            _, count = self._repo.query({"status": status}, limit=0)
            result[status] = count
        return result
