from app.models import Status

ALLOWED_TRANSITIONS = {
    Status.open: {Status.in_progress, Status.rejected},
    Status.in_progress: {Status.resolved, Status.rejected},
    Status.resolved: set(),
    Status.rejected: set(),
}


def validate_transition(current: Status, new: Status) -> bool:
    if current == new:
        return False
    return new in ALLOWED_TRANSITIONS.get(current, set())