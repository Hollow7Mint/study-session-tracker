"""Study Session Tracker — exception types."""

class StudySessionTrackerError(Exception):
    """Base exception for all Study Session Tracker errors."""

    def __init__(self, message: str, code: int = 0) -> None:
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {super().__str__()}"


class GoalNotFoundError(StudySessionTrackerError):
    """Raised when a Goal record cannot be located."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Goal {record_id!r} not found", code=404)
        self.record_id = record_id


class GoalValidationError(StudySessionTrackerError):
    """Raised when a Goal fails field validation."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"Invalid {field!r}: {reason}", code=422)
        self.field  = field
        self.reason = reason


class StudySessionTrackerConflictError(StudySessionTrackerError):
    """Raised on duplicate or conflicting Study Session Tracker state."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Conflict: {detail}", code=409)


def raise_if_none(value: object, label: str = "Goal") -> object:
    """Raise GoalNotFoundError if *value* is None."""
    if value is None:
        raise GoalNotFoundError(label)
    return value
