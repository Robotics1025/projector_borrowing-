import pytest
from uuid import uuid4

from projector_borrowing.domain.projectors import (
    InvalidProjectorTransitionError,
    Projector,
    ProjectorStatus,
    ProjectorType,
)


def test_new_projector_is_available(standard_projector: Projector) -> None:
    assert standard_projector.is_available()
    assert standard_projector.status is ProjectorStatus.AVAILABLE
    assert standard_projector.version == 0


def test_borrow_and_return_update_version(
    standard_projector: Projector,
) -> None:
    standard_projector.mark_borrowed()
    assert standard_projector.status is ProjectorStatus.BORROWED
    assert standard_projector.version == 1
    standard_projector.mark_available()
    assert standard_projector.is_available()
    assert standard_projector.version == 2


def test_maintenance_lifecycle(standard_projector: Projector) -> None:
    standard_projector.mark_for_maintenance()
    assert standard_projector.status is ProjectorStatus.MAINTENANCE
    standard_projector.complete_maintenance()
    assert standard_projector.is_available()
    assert standard_projector.version == 2


def test_rejects_invalid_transition(
    standard_projector: Projector,
) -> None:
    with pytest.raises(InvalidProjectorTransitionError):
        standard_projector.mark_available()
    standard_projector.mark_borrowed()
    with pytest.raises(InvalidProjectorTransitionError):
        standard_projector.mark_borrowed()
    with pytest.raises(InvalidProjectorTransitionError):
        standard_projector.mark_for_maintenance()


def test_rejects_duplicate_maintenance_transition(
    standard_projector: Projector,
) -> None:
    standard_projector.mark_for_maintenance()

    with pytest.raises(InvalidProjectorTransitionError):
        standard_projector.mark_for_maintenance()


def test_rejects_completing_maintenance_when_available(
    standard_projector: Projector,
) -> None:
    with pytest.raises(InvalidProjectorTransitionError):
        standard_projector.complete_maintenance()


@pytest.mark.parametrize(
    ("projector_id", "projector_type", "status", "version", "message"),
    [
        ("bad", ProjectorType.STANDARD, ProjectorStatus.AVAILABLE, 0, "projector_id"),
        (uuid4(), "STANDARD", ProjectorStatus.AVAILABLE, 0, "projector_type"),
        (uuid4(), ProjectorType.STANDARD, "AVAILABLE", 0, "status"),
        (uuid4(), ProjectorType.STANDARD, ProjectorStatus.AVAILABLE, True, "version"),
        (uuid4(), ProjectorType.STANDARD, ProjectorStatus.AVAILABLE, -1, "negative"),
    ],
)
def test_rejects_invalid_constructor_values(
    projector_id: object,
    projector_type: object,
    status: object,
    version: object,
    message: str,
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        Projector(  # type: ignore[arg-type]
            projector_id,
            projector_type,
            status,
            version,
        )


def test_identity_and_representation() -> None:
    projector_id = uuid4()
    first = Projector(projector_id, ProjectorType.STANDARD)
    second = Projector(projector_id, ProjectorType.PREMIUM)

    assert first == second
    assert first != object()
    assert hash(first) == hash(second)
    assert "Projector(" in repr(first)
