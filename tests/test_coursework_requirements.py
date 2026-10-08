from datetime import date, timedelta
from uuid import uuid4

import pytest

from projector_borrowing.application import (
    BorrowerNotFoundError,
    IssueLoan,
    IssueLoanCommand,
    LoanIssuedHandler,
    RequestLoan,
    RequestLoanCommand,
)
from projector_borrowing.domain import (
    Borrower,
    BorrowerRole,
    BorrowingEligibilityService,
    BorrowingPeriod,
    InvalidBorrowingPeriodError,
    LoanLimitExceededError,
    LoanStatus,
    Projector,
    ProjectorStatus,
    ProjectorType,
)
from projector_borrowing.domain.borrowing import (
    LoanIssued,
    PremiumProjectorRestrictedError,
)
from projector_borrowing.domain.projectors import (
    InvalidProjectorTransitionError,
)
from projector_borrowing.infrastructure import (
    InMemoryBorrowerRepository,
    InMemoryProjectorRepository,
)


def test_t1_br1_accepts_seven_day_boundary_and_rejects_eight_days() -> None:
    start = date(2026, 10, 8)
    assert BorrowingPeriod(start, start + timedelta(days=7)).duration_in_days() == 7
    with pytest.raises(InvalidBorrowingPeriodError):
        BorrowingPeriod(start, start + timedelta(days=8))


def test_t2_br2_projector_allows_only_valid_state_change() -> None:
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    projector.mark_borrowed()
    assert projector.status is ProjectorStatus.BORROWED
    with pytest.raises(InvalidProjectorTransitionError):
        projector.mark_borrowed()


def test_t3_br3_borrower_rejects_third_open_loan() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    period = BorrowingPeriod(date(2026, 10, 8), date(2026, 10, 9))
    borrower.request_loan(uuid4(), period)
    borrower.request_loan(uuid4(), period)
    with pytest.raises(LoanLimitExceededError):
        borrower.request_loan(uuid4(), period)


def test_t4_br4_student_is_ineligible_for_premium_projector() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STUDENT)
    projector = Projector(uuid4(), ProjectorType.PREMIUM)
    with pytest.raises(PremiumProjectorRestrictedError):
        BorrowingEligibilityService.check_eligibility(borrower, projector)


def test_t5_br5_issuing_raises_loan_issued_event() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    projector_id = uuid4()
    period = BorrowingPeriod(date(2026, 10, 8), date(2026, 10, 9))
    loan_id = borrower.request_loan(projector_id, period)
    borrower.issue_loan(loan_id)
    events = borrower.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], LoanIssued)
    assert events[0].projector_id == projector_id


def test_t6_br6_request_rejects_missing_borrower_lookup() -> None:
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    use_case = RequestLoan(
        InMemoryBorrowerRepository(),
        InMemoryProjectorRepository((projector,)),
    )
    with pytest.raises(BorrowerNotFoundError):
        use_case.execute(
            RequestLoanCommand(
                uuid4(),
                projector.projector_id,
                date(2026, 10, 8),
                date(2026, 10, 9),
            )
        )


def test_t7_main_use_case_handles_event_and_changes_projector() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    borrowers = InMemoryBorrowerRepository((borrower,))
    projectors = InMemoryProjectorRepository((projector,))
    period = BorrowingPeriod(date(2026, 10, 8), date(2026, 10, 9))
    loan_id = borrower.request_loan(projector.projector_id, period)
    borrowers.save(borrower)

    result = IssueLoan(borrowers, projectors).execute(
        IssueLoanCommand(borrower.borrower_id, loan_id)
    )

    stored_projector = projectors.get_by_id(projector.projector_id)
    assert result.status is LoanStatus.ACTIVE
    assert stored_projector is not None
    assert stored_projector.status is ProjectorStatus.BORROWED


def test_t8_projector_rejects_event_follow_up_and_keeps_state() -> None:
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    projector.mark_borrowed()
    projectors = InMemoryProjectorRepository((projector,))
    event = LoanIssued(
        loan_id=uuid4(),
        borrower_id=uuid4(),
        projector_id=projector.projector_id,
        due_date=date(2026, 10, 9),
    )

    with pytest.raises(InvalidProjectorTransitionError):
        LoanIssuedHandler(projectors).handle(event)

    stored_projector = projectors.get_by_id(projector.projector_id)
    assert stored_projector is not None
    assert stored_projector.status is ProjectorStatus.BORROWED
    assert stored_projector.version == 1
