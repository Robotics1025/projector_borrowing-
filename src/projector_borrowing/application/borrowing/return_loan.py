from ...domain.borrowing import BorrowerRepository
from ...domain.projectors import ProjectorRepository
from ._loaders import load_borrower, load_projector
from .dto import LoanResult, ReturnLoanCommand


class ReturnLoan:
    def __init__(
        self,
        borrower_repository: BorrowerRepository,
        projector_repository: ProjectorRepository,
    ) -> None:
        self._borrower_repository = borrower_repository
        self._projector_repository = projector_repository

    def execute(self, command: ReturnLoanCommand) -> LoanResult:
        borrower = load_borrower(
            self._borrower_repository,
            command.borrower_id,
        )
        loan = borrower.get_loan(command.loan_id)
        projector = load_projector(
            self._projector_repository,
            loan.projector_id,
        )

        expected_projector_version = projector.version
        borrower.return_loan(loan.id)
        projector.mark_available()
        self._projector_repository.save(
            projector,
            expected_version=expected_projector_version,
        )
        self._borrower_repository.save(borrower)

        return LoanResult.from_loan(loan)
