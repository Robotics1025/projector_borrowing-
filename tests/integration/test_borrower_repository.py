from uuid import uuid4

import pytest

from projector_borrowing.domain import Borrower, BorrowerRole
from projector_borrowing.infrastructure import InMemoryBorrowerRepository


def test_saves_and_returns_detached_borrower_copy() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STUDENT)
    repository = InMemoryBorrowerRepository()

    repository.save(borrower)
    loaded = repository.get_by_id(borrower.borrower_id)

    assert loaded == borrower
    assert loaded is not borrower


def test_returns_none_for_unknown_borrower() -> None:
    assert InMemoryBorrowerRepository().get_by_id(uuid4()) is None


def test_rejects_invalid_borrower() -> None:
    with pytest.raises(TypeError, match="Borrower"):
        InMemoryBorrowerRepository().save(object())  # type: ignore[arg-type]
