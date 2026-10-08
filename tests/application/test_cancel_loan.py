from uuid import uuid4

from projector_borrowing.application import CancelLoan, CancelLoanCommand
from projector_borrowing.domain.borrowing import (
    Borrower,
    BorrowingPeriod,
    LoanStatus,
)


def test_cancels_and_saves_pending_loan(
    student_borrower: Borrower,
    borrowing_period: BorrowingPeriod,
    borrower_repository,
) -> None:
    loan_id = student_borrower.request_loan(
        uuid4(),
        borrowing_period,
    )
    use_case = CancelLoan(borrower_repository)

    result = use_case.execute(
        CancelLoanCommand(student_borrower.borrower_id, loan_id)
    )

    assert result.status is LoanStatus.CANCELLED
    assert borrower_repository.saved == [student_borrower]
