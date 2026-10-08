from datetime import date, timedelta
from uuid import uuid4

from projector_borrowing.application import (
    IssueLoan,
    IssueLoanCommand,
    RequestLoan,
    RequestLoanCommand,
    ReturnLoan,
    ReturnLoanCommand,
)
from projector_borrowing.domain import (
    Borrower,
    BorrowerRole,
    LoanStatus,
    Projector,
    ProjectorStatus,
    ProjectorType,
)
from projector_borrowing.infrastructure import (
    InMemoryBorrowerRepository,
    InMemoryProjectorRepository,
)


def test_complete_request_issue_return_workflow() -> None:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    borrowers = InMemoryBorrowerRepository((borrower,))
    projectors = InMemoryProjectorRepository((projector,))
    start_date = date.today()

    requested = RequestLoan(borrowers, projectors).execute(
        RequestLoanCommand(
            borrower.borrower_id,
            projector.projector_id,
            start_date,
            start_date + timedelta(days=3),
        )
    )
    issued = IssueLoan(borrowers, projectors).execute(
        IssueLoanCommand(borrower.borrower_id, requested.loan_id)
    )
    returned = ReturnLoan(borrowers, projectors).execute(
        ReturnLoanCommand(borrower.borrower_id, requested.loan_id)
    )

    assert requested.status is LoanStatus.PENDING
    assert issued.status is LoanStatus.ACTIVE
    assert returned.status is LoanStatus.RETURNED
    stored_projector = projectors.get_by_id(projector.projector_id)
    assert stored_projector is not None
    assert stored_projector.status is ProjectorStatus.AVAILABLE
    assert stored_projector.version == 2
