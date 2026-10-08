from datetime import date, timedelta
from uuid import uuid4

import pytest

from projector_borrowing.application import IssueLoan, IssueLoanCommand
from projector_borrowing.domain import (
    Borrower,
    BorrowerRole,
    BorrowingEligibilityService,
    BorrowingPeriod,
    InvalidBorrowingPeriodError,
    LoanLimitExceededError,
    Projector,
    ProjectorType,
)
from projector_borrowing.domain.borrowing import (
    LoanIssued,
    LoanReturned,
    PremiumProjectorRestrictedError,
    ProjectorUnavailableError,
)
from projector_borrowing.domain.projectors import ProjectorConcurrencyError
from projector_borrowing.infrastructure import (
    InMemoryBorrowerRepository,
    InMemoryProjectorRepository,
)


def test_br1_duration_is_one_to_seven_days() -> None:
    today = date.today()
    with pytest.raises(InvalidBorrowingPeriodError):
        BorrowingPeriod(today, today + timedelta(days=8))


def test_br2_only_available_projector_can_be_issued() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    projector.mark_borrowed()
    with pytest.raises(ProjectorUnavailableError):
        BorrowingEligibilityService.check_eligibility(borrower, projector)


def test_br3_maximum_two_open_loans() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    period = BorrowingPeriod(date.today(), date.today() + timedelta(days=1))
    borrower.request_loan(uuid4(), period)
    borrower.request_loan(uuid4(), period)
    with pytest.raises(LoanLimitExceededError):
        borrower.request_loan(uuid4(), period)


def test_br4_student_cannot_borrow_premium_projector() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STUDENT)
    projector = Projector(uuid4(), ProjectorType.PREMIUM)
    with pytest.raises(PremiumProjectorRestrictedError):
        BorrowingEligibilityService.check_eligibility(borrower, projector)


def test_br5_issue_and_return_record_events() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    period = BorrowingPeriod(date.today(), date.today() + timedelta(days=1))
    loan_id = borrower.request_loan(uuid4(), period)
    borrower.issue_loan(loan_id)
    borrower.return_loan(loan_id)
    events = borrower.pull_events()
    assert isinstance(events[0], LoanIssued)
    assert isinstance(events[1], LoanReturned)


def test_br6_stale_projector_write_is_rejected() -> None:
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    repository = InMemoryProjectorRepository((projector,))
    current = repository.get_by_id(projector.projector_id)
    stale = repository.get_by_id(projector.projector_id)
    assert current is not None
    assert stale is not None
    current.mark_borrowed()
    repository.save(current, expected_version=0)
    stale.mark_for_maintenance()
    with pytest.raises(ProjectorConcurrencyError):
        repository.save(stale, expected_version=0)
