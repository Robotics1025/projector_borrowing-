from projector_borrowing.application import ReturnLoan, ReturnLoanCommand
from projector_borrowing.domain.borrowing import (
    Borrower,
    BorrowingPeriod,
    LoanStatus,
)
from projector_borrowing.domain.projectors import Projector, ProjectorStatus


def test_returns_loan_and_marks_projector_available(
    student_borrower: Borrower,
    standard_projector: Projector,
    borrowing_period: BorrowingPeriod,
    borrower_repository,
    projector_repository,
) -> None:
    loan_id = student_borrower.request_loan(
        standard_projector.projector_id,
        borrowing_period,
    )
    student_borrower.issue_loan(loan_id)
    standard_projector.mark_borrowed()
    use_case = ReturnLoan(borrower_repository, projector_repository)

    result = use_case.execute(
        ReturnLoanCommand(student_borrower.borrower_id, loan_id)
    )

    assert result.status is LoanStatus.RETURNED
    assert standard_projector.status is ProjectorStatus.AVAILABLE
    assert borrower_repository.saved == [student_borrower]
    assert projector_repository.saved == [standard_projector]
