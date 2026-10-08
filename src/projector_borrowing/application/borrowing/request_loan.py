from ...domain.borrowing import (
    BorrowerRepository,
    BorrowingEligibilityService,
    BorrowingPeriod,
)
from ...domain.projectors import ProjectorRepository
from ._loaders import load_borrower, load_projector
from .dto import LoanResult, RequestLoanCommand


class RequestLoan:
    def __init__(
        self,
        borrower_repository: BorrowerRepository,
        projector_repository: ProjectorRepository,
    ) -> None:
        self._borrower_repository = borrower_repository
        self._projector_repository = projector_repository

    def execute(self, command: RequestLoanCommand) -> LoanResult:
        borrower = load_borrower(
            self._borrower_repository,
            command.borrower_id,
        )
        projector = load_projector(
            self._projector_repository,
            command.projector_id,
        )
        BorrowingEligibilityService.check_eligibility(borrower, projector)

        period = BorrowingPeriod(command.start_date, command.due_date)
        loan_id = borrower.request_loan(projector.projector_id, period)
        self._borrower_repository.save(borrower)

        return LoanResult.from_loan(borrower.get_loan(loan_id))
