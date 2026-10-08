from datetime import date
from uuid import uuid4

import pytest

from projector_borrowing.domain.borrowing import (
    Borrower,
    BorrowerRole,
    BorrowingPeriod,
)
from projector_borrowing.domain.projectors import Projector, ProjectorType


class InMemoryBorrowerRepository:
    def __init__(self, borrowers: list[Borrower] | None = None) -> None:
        self.items = {
            borrower.borrower_id: borrower for borrower in borrowers or []
        }
        self.saved: list[Borrower] = []

    def get_by_id(self, borrower_id):
        return self.items.get(borrower_id)

    def save(self, borrower: Borrower) -> None:
        self.items[borrower.borrower_id] = borrower
        self.saved.append(borrower)


class InMemoryProjectorRepository:
    def __init__(self, projectors: list[Projector] | None = None) -> None:
        self.items = {
            projector.projector_id: projector
            for projector in projectors or []
        }
        self.saved: list[Projector] = []

    def get_by_id(self, projector_id):
        return self.items.get(projector_id)

    def save(
        self,
        projector: Projector,
        *,
        expected_version: int | None = None,
    ) -> None:
        self.items[projector.projector_id] = projector
        self.saved.append(projector)


@pytest.fixture
def borrowing_period() -> BorrowingPeriod:
    return BorrowingPeriod(date(2026, 10, 8), date(2026, 10, 11))


@pytest.fixture
def student_borrower() -> Borrower:
    return Borrower(uuid4(), BorrowerRole.STUDENT)


@pytest.fixture
def staff_borrower() -> Borrower:
    return Borrower(uuid4(), BorrowerRole.STAFF)


@pytest.fixture
def standard_projector() -> Projector:
    return Projector(uuid4(), ProjectorType.STANDARD)


@pytest.fixture
def premium_projector() -> Projector:
    return Projector(uuid4(), ProjectorType.PREMIUM)


@pytest.fixture
def borrower_repository(
    student_borrower: Borrower,
) -> InMemoryBorrowerRepository:
    return InMemoryBorrowerRepository([student_borrower])


@pytest.fixture
def projector_repository(
    standard_projector: Projector,
) -> InMemoryProjectorRepository:
    return InMemoryProjectorRepository([standard_projector])
