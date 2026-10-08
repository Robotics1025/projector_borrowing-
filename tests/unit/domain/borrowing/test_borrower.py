from datetime import timezone
from uuid import uuid4

import pytest

from projector_borrowing.domain.borrowing import (
    Borrower,
    BorrowerRole,
    BorrowingPeriod,
    DomainEvent,
    InvalidLoanTransitionError,
    LoanIssued,
    LoanLimitExceededError,
    LoanNotFoundError,
    LoanReturned,
    LoanStatus,
    Loan,
)


def test_requests_pending_loan(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    projector_id = uuid4()
    loan_id = student_borrower.request_loan(projector_id, borrowing_period)
    assert len(student_borrower.loans) == 1
    loan = student_borrower.loans[0]
    assert loan.id == loan_id
    assert loan.projector_id == projector_id
    assert loan.status is LoanStatus.PENDING


def test_limits_borrower_to_two_open_loans(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    student_borrower.request_loan(uuid4(), borrowing_period)
    student_borrower.request_loan(uuid4(), borrowing_period)
    with pytest.raises(LoanLimitExceededError):
        student_borrower.request_loan(uuid4(), borrowing_period)


def test_cancelled_loan_frees_capacity(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    first_loan_id = student_borrower.request_loan(uuid4(), borrowing_period)
    student_borrower.request_loan(uuid4(), borrowing_period)
    student_borrower.cancel_loan(first_loan_id)
    student_borrower.request_loan(uuid4(), borrowing_period)
    assert student_borrower.pending_and_active_count() == 2


def test_issue_and_return_record_events(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    projector_id = uuid4()
    loan_id = student_borrower.request_loan(projector_id, borrowing_period)
    student_borrower.issue_loan(loan_id)
    student_borrower.return_loan(loan_id)
    events = student_borrower.pull_events()
    assert len(events) == 2
    assert isinstance(events[0], LoanIssued)
    assert isinstance(events[0], DomainEvent)
    assert events[0].loan_id == loan_id
    assert events[0].due_date == borrowing_period.due_date
    assert events[0].occurred_at.utcoffset() == timezone.utc.utcoffset(None)
    assert isinstance(events[1], LoanReturned)
    assert student_borrower.pull_events() == []


def test_rejects_invalid_transition(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    loan_id = student_borrower.request_loan(uuid4(), borrowing_period)
    with pytest.raises(InvalidLoanTransitionError):
        student_borrower.return_loan(loan_id)


def test_rejects_unknown_loan(student_borrower: Borrower) -> None:
    with pytest.raises(LoanNotFoundError):
        student_borrower.issue_loan(uuid4())


def test_rejects_unknown_loan_after_searching_existing_loans(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    student_borrower.request_loan(uuid4(), borrowing_period)
    with pytest.raises(LoanNotFoundError):
        student_borrower.issue_loan(uuid4())


def test_finds_a_later_loan_in_collection(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    student_borrower.request_loan(uuid4(), borrowing_period)
    second_loan_id = student_borrower.request_loan(uuid4(), borrowing_period)

    student_borrower.issue_loan(second_loan_id)

    assert student_borrower.loans[1].status is LoanStatus.ACTIVE


@pytest.mark.parametrize(
    ("borrower_id", "role", "message"),
    [
        ("bad", BorrowerRole.STUDENT, "borrower_id"),
        (uuid4(), "STUDENT", "role"),
    ],
)
def test_rejects_invalid_identity_or_role(
    borrower_id: object,
    role: object,
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        Borrower(borrower_id, role)  # type: ignore[arg-type]


def test_rejects_invalid_restored_loans(
    borrowing_period: BorrowingPeriod,
) -> None:
    borrower_id = uuid4()
    with pytest.raises(TypeError, match="Loan instances"):
        Borrower(borrower_id, BorrowerRole.STAFF, [object()])  # type: ignore[list-item]

    loan = Loan(uuid4(), uuid4(), borrowing_period)
    with pytest.raises(ValueError, match="unique"):
        Borrower(borrower_id, BorrowerRole.STAFF, [loan, loan])

    open_loans = [
        Loan(uuid4(), uuid4(), borrowing_period)
        for _ in range(Borrower.MAX_OPEN_LOANS + 1)
    ]
    with pytest.raises(LoanLimitExceededError):
        Borrower(borrower_id, BorrowerRole.STAFF, open_loans)


def test_rejects_invalid_request_values(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
) -> None:
    with pytest.raises(TypeError, match="projector_id"):
        student_borrower.request_loan("bad", borrowing_period)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="borrowing_period"):
        student_borrower.request_loan(uuid4(), object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="loan_id"):
        student_borrower.issue_loan("bad")  # type: ignore[arg-type]


def test_identity_accessors_and_representation() -> None:
    borrower_id = uuid4()
    borrower = Borrower(borrower_id, BorrowerRole.STAFF)
    same_borrower = Borrower(borrower_id, BorrowerRole.STUDENT)

    assert borrower.get_borrower_id() == borrower_id
    assert borrower.get_role() is BorrowerRole.STAFF
    assert borrower == same_borrower
    assert borrower != object()
    assert hash(borrower) == hash(same_borrower)
    assert "Borrower(" in repr(borrower)
