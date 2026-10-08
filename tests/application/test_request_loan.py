from datetime import date
from uuid import uuid4

import pytest

from projector_borrowing.application import (
    BorrowerNotFoundError,
    ProjectorNotFoundError,
    RequestLoan,
    RequestLoanCommand,
)
from projector_borrowing.domain.borrowing import Borrower, LoanStatus
from projector_borrowing.domain.projectors import Projector


def test_requests_and_saves_pending_loan(
    student_borrower: Borrower,
    standard_projector: Projector,
    borrower_repository,
    projector_repository,
) -> None:
    use_case = RequestLoan(borrower_repository, projector_repository)
    command = RequestLoanCommand(
        borrower_id=student_borrower.borrower_id,
        projector_id=standard_projector.projector_id,
        start_date=date(2026, 10, 8),
        due_date=date(2026, 10, 11),
    )

    result = use_case.execute(command)

    assert result.status is LoanStatus.PENDING
    assert result.projector_id == standard_projector.projector_id
    assert result.start_date == command.start_date
    assert result.due_date == command.due_date
    assert borrower_repository.saved == [student_borrower]
    assert projector_repository.saved == []


def test_rejects_unknown_borrower(
    standard_projector: Projector,
    borrower_repository,
    projector_repository,
) -> None:
    borrower_repository.items.clear()
    use_case = RequestLoan(borrower_repository, projector_repository)

    with pytest.raises(BorrowerNotFoundError, match="borrower"):
        use_case.execute(
            RequestLoanCommand(
                uuid4(),
                standard_projector.projector_id,
                date(2026, 10, 8),
                date(2026, 10, 11),
            )
        )


def test_rejects_unknown_projector(
    student_borrower: Borrower,
    borrower_repository,
    projector_repository,
) -> None:
    projector_repository.items.clear()
    use_case = RequestLoan(borrower_repository, projector_repository)

    with pytest.raises(ProjectorNotFoundError, match="projector"):
        use_case.execute(
            RequestLoanCommand(
                student_borrower.borrower_id,
                uuid4(),
                date(2026, 10, 8),
                date(2026, 10, 11),
            )
        )
