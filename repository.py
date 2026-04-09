"""Study Session Tracker — Note repository layer."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class StudyRepository:
    """Note repository for the Study Session Tracker application."""

    def __init__(
        self,
        store: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._store = store
        self._cfg   = config or {}
        self._notes = self._cfg.get("notes", None)
        logger.debug("%s initialised", self.__class__.__name__)

    def pause_note(
        self, notes: Any, focus_score: Any, **extra: Any
    ) -> Dict[str, Any]:
        """Create and persist a new Note record."""
        now = datetime.now(timezone.utc).isoformat()
        record: Dict[str, Any] = {
            "id":         str(uuid.uuid4()),
            "notes": notes,
            "focus_score": focus_score,
            "status":     "active",
            "created_at": now,
            **extra,
        }
        saved = self._store.put(record)
        logger.info("pause_note: created %s", saved["id"])
        return saved

    def get_note(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Note by its *record_id*."""
        record = self._store.get(record_id)
        if record is None:
            logger.debug("get_note: %s not found", record_id)
        return record

    def export_note(
        self, record_id: str, **changes: Any
    ) -> Dict[str, Any]:
        """Apply *changes* to an existing Note."""
        record = self._store.get(record_id)
        if record is None:
            raise KeyError(f"Note {record_id!r} not found")
        record.update(changes)
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self._store.put(record)

    def review_note(self, record_id: str) -> bool:
        """Remove a Note; returns True on success."""
        if self._store.get(record_id) is None:
            return False
        self._store.delete(record_id)
        logger.info("review_note: removed %s", record_id)
        return True

    def list_notes(
        self,
        status: Optional[str] = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return paginated Note records."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        results = self._store.find(query, limit=limit, offset=offset)
        logger.debug("list_notes: %d results", len(results))
        return results

    def iter_notes(
        self, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """Yield all Note records in batches of *batch_size*."""
        offset = 0
        while True:
            page = self.list_notes(limit=batch_size, offset=offset)
            if not page:
                break
            yield from page
            if len(page) < batch_size:
                break
            offset += batch_size
