from uuid import uuid4

import pytest

from projector_borrowing.domain import Projector, ProjectorType
from projector_borrowing.domain.projectors import ProjectorConcurrencyError
from projector_borrowing.infrastructure import InMemoryProjectorRepository


def test_saves_and_returns_detached_projector_copy() -> None:
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    repository = InMemoryProjectorRepository((projector,))

    loaded = repository.get_by_id(projector.projector_id)

    assert loaded == projector
    assert loaded is not projector


def test_returns_none_for_unknown_projector() -> None:
    assert InMemoryProjectorRepository().get_by_id(uuid4()) is None


def test_rejects_stale_projector_update() -> None:
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    repository = InMemoryProjectorRepository((projector,))
    first_writer = repository.get_by_id(projector.projector_id)
    stale_writer = repository.get_by_id(projector.projector_id)
    assert first_writer is not None
    assert stale_writer is not None

    first_writer.mark_borrowed()
    repository.save(first_writer, expected_version=0)
    stale_writer.mark_for_maintenance()

    with pytest.raises(ProjectorConcurrencyError, match="version conflict"):
        repository.save(stale_writer, expected_version=0)


@pytest.mark.parametrize("expected_version", [-1, True, "zero"])
def test_rejects_invalid_expected_version(expected_version: object) -> None:
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    repository = InMemoryProjectorRepository((projector,))

    with pytest.raises(ValueError, match="non-negative integer"):
        repository.save(  # type: ignore[arg-type]
            projector,
            expected_version=expected_version,
        )


def test_rejects_invalid_projector() -> None:
    with pytest.raises(TypeError, match="Projector"):
        InMemoryProjectorRepository().save(object())  # type: ignore[arg-type]
