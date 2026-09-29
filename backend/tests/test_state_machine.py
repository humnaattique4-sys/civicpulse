from app.models import Status
from app.services.state_machine import validate_transition, ALLOWED_TRANSITIONS


def test_open_to_in_progress_is_allowed():
    assert validate_transition(Status.open, Status.in_progress) is True


def test_open_to_rejected_is_allowed():
    assert validate_transition(Status.open, Status.rejected) is True


def test_open_cannot_jump_to_resolved():
    assert validate_transition(Status.open, Status.resolved) is False


def test_in_progress_to_resolved_is_allowed():
    assert validate_transition(Status.in_progress, Status.resolved) is True


def test_terminal_states_have_no_transitions():
    assert ALLOWED_TRANSITIONS[Status.resolved] == set()
    assert ALLOWED_TRANSITIONS[Status.rejected] == set()


def test_same_state_is_not_a_transition():
    assert validate_transition(Status.open, Status.open) is False