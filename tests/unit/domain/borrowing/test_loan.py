from uuid import uuid4

import pytest

from projector_borrowing.domain.borrowing import (
    BorrowingPeriod,
    InvalidLoanTransitionError,
    Loan,
    LoanStatus,
)


def test_new_loan_is_pending(borrowing_period: BorrowingPeriod) -> None:
    loan = Loan(uuid4(), uuid4(), borrowing_period)
    assert loan.status is LoanStatus.PENDING
    assert loan.borrowing_period == borrowing_period


def test_pending_loan_can_be_issued_and_returned(
    borrowing_period: BorrowingPeriod,
) -> None:
    loan = Loan(uuid4(), uuid4(), borrowing_period)
    loan.mark_issued()
    assert loan.status is LoanStatus.ACTIVE
    loan.mark_returned()
    assert loan.status is LoanStatus.RETURNED


def test_pending_loan_can_be_cancelled(
    borrowing_period: BorrowingPeriod,
) -> None:
    loan = Loan(uuid4(), uuid4(), borrowing_period)
    loan.mark_cancelled()
    assert loan.status is LoanStatus.CANCELLED


def test_rejects_invalid_transition(
    borrowing_period: BorrowingPeriod,
) -> None:
    loan = Loan(uuid4(), uuid4(), borrowing_period)
    with pytest.raises(InvalidLoanTransitionError):
        loan.mark_returned()


def test_rejects_issue_and_cancel_after_loan_is_active(
    borrowing_period: BorrowingPeriod,
) -> None:
    loan = Loan(uuid4(), uuid4(), borrowing_period)
    loan.mark_issued()

    with pytest.raises(InvalidLoanTransitionError):
        loan.mark_issued()
    with pytest.raises(InvalidLoanTransitionError):
        loan.mark_cancelled()


@pytest.mark.parametrize(
    ("loan_id", "projector_id", "period", "status", "message"),
    [
        ("bad", uuid4(), "period", LoanStatus.PENDING, "loan_id"),
        (uuid4(), "bad", "period", LoanStatus.PENDING, "projector_id"),
        (uuid4(), uuid4(), "bad", LoanStatus.PENDING, "borrowing_period"),
        (uuid4(), uuid4(), "period", "PENDING", "status"),
    ],
)
def test_rejects_invalid_constructor_values(
    loan_id: object,
    projector_id: object,
    period: object,
    status: object,
    message: str,
    borrowing_period: BorrowingPeriod,
) -> None:
    actual_period = borrowing_period if period == "period" else period

    with pytest.raises(TypeError, match=message):
        Loan(  # type: ignore[arg-type]
            loan_id,
            projector_id,
            actual_period,
            status,
        )


def test_identity_is_based_on_loan_id(
    borrowing_period: BorrowingPeriod,
) -> None:
    loan_id = uuid4()
    first = Loan(loan_id, uuid4(), borrowing_period)
    second = Loan(loan_id, uuid4(), borrowing_period)
    assert first == second
    assert hash(first) == hash(second)
    assert first != object()
    assert "Loan(" in repr(first)
