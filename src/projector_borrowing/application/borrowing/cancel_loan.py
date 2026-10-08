from ...domain.borrowing import BorrowerRepository
from ._loaders import load_borrower
from .dto import CancelLoanCommand, LoanResult


class CancelLoan:
    def __init__(self, borrower_repository: BorrowerRepository) -> None:
        self._borrower_repository = borrower_repository

    def execute(self, command: CancelLoanCommand) -> LoanResult:
        borrower = load_borrower(
            self._borrower_repository,
            command.borrower_id,
        )
        borrower.cancel_loan(command.loan_id)
        loan = borrower.get_loan(command.loan_id)
        self._borrower_repository.save(borrower)
        return LoanResult.from_loan(loan)
