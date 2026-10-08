from uuid import uuid4

from projector_borrowing.application import IssueLoan, IssueLoanCommand
from projector_borrowing.domain.borrowing import (
    Borrower,
    BorrowingPeriod,
    LoanStatus,
)
from projector_borrowing.domain.projectors import Projector, ProjectorStatus


def test_issues_loan_and_marks_projector_borrowed(
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
    use_case = IssueLoan(borrower_repository, projector_repository)

    result = use_case.execute(
        IssueLoanCommand(student_borrower.borrower_id, loan_id)
    )

    assert result.status is LoanStatus.ACTIVE
    assert standard_projector.status is ProjectorStatus.BORROWED
    assert borrower_repository.saved == [student_borrower]
    assert projector_repository.saved == [standard_projector]


def test_issuing_existing_loan_does_not_reapply_capacity_limit(
    student_borrower: Borrower,
    standard_projector: Projector,
    borrowing_period: BorrowingPeriod,
    borrower_repository,
    projector_repository,
) -> None:
    first_loan_id = student_borrower.request_loan(
        standard_projector.projector_id,
        borrowing_period,
    )
    student_borrower.request_loan(uuid4(), borrowing_period)

    result = IssueLoan(
        borrower_repository,
        projector_repository,
    ).execute(IssueLoanCommand(student_borrower.borrower_id, first_loan_id))

    assert result.status is LoanStatus.ACTIVE
