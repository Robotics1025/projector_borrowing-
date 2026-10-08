from dataclasses import dataclass
from datetime import date
from uuid import UUID

from ...domain.borrowing import Loan, LoanStatus


@dataclass(frozen=True, slots=True)
class RequestLoanCommand:
    borrower_id: UUID
    projector_id: UUID
    start_date: date
    due_date: date


@dataclass(frozen=True, slots=True)
class IssueLoanCommand:
    borrower_id: UUID
    loan_id: UUID


@dataclass(frozen=True, slots=True)
class ReturnLoanCommand:
    borrower_id: UUID
    loan_id: UUID


@dataclass(frozen=True, slots=True)
class CancelLoanCommand:
    borrower_id: UUID
    loan_id: UUID


@dataclass(frozen=True, slots=True)
class LoanResult:
    loan_id: UUID
    projector_id: UUID
    status: LoanStatus
    start_date: date
    due_date: date

    @classmethod
    def from_loan(cls, loan: Loan) -> "LoanResult":
        return cls(
            loan_id=loan.id,
            projector_id=loan.projector_id,
            status=loan.status,
            start_date=loan.borrowing_period.start_date,
            due_date=loan.borrowing_period.due_date,
        )
