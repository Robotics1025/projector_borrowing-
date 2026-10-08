from ...domain.borrowing import BorrowerRepository, BorrowingEligibilityService
from ...domain.projectors import ProjectorRepository
from ._loaders import load_borrower, load_projector
from .dto import IssueLoanCommand, LoanResult


class IssueLoan:
    def __init__(
        self,
        borrower_repository: BorrowerRepository,
        projector_repository: ProjectorRepository,
    ) -> None:
        self._borrower_repository = borrower_repository
        self._projector_repository = projector_repository

    def execute(self, command: IssueLoanCommand) -> LoanResult:
        borrower = load_borrower(
            self._borrower_repository,
            command.borrower_id,
        )
        loan = borrower.get_loan(command.loan_id)
        projector = load_projector(
            self._projector_repository,
            loan.projector_id,
        )
        BorrowingEligibilityService.check_eligibility(
            borrower,
            projector,
            enforce_loan_limit=False,
        )

        expected_projector_version = projector.version
        borrower.issue_loan(loan.id)
        projector.mark_borrowed()
        self._projector_repository.save(
            projector,
            expected_version=expected_projector_version,
        )
        self._borrower_repository.save(borrower)

        return LoanResult.from_loan(loan)
