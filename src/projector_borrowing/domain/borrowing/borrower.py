from collections.abc import Iterable
from typing import ClassVar
from uuid import UUID, uuid4

from .entity import Loan
from .enums import BorrowerRole, LoanStatus
from .events import DomainEvent, LoanIssued, LoanReturned
from .exceptions import LoanLimitExceededError, LoanNotFoundError
from .valueobject import BorrowingPeriod


class Borrower:
    MAX_OPEN_LOANS: ClassVar[int] = 2

    def __init__(
        self,
        borrower_id: UUID,
        role: BorrowerRole,
        loans: Iterable[Loan] = (),
    ) -> None:
        if not isinstance(borrower_id, UUID):
            raise TypeError("borrower_id must be a UUID")
        if not isinstance(role, BorrowerRole):
            raise TypeError("role must be a BorrowerRole")

        restored_loans = list(loans)
        if not all(isinstance(loan, Loan) for loan in restored_loans):
            raise TypeError("loans must contain only Loan instances")
        if len({loan.id for loan in restored_loans}) != len(restored_loans):
            raise ValueError("loan IDs must be unique within a borrower")
        open_statuses = {LoanStatus.PENDING, LoanStatus.ACTIVE}
        open_loan_count = sum(
            loan.status in open_statuses for loan in restored_loans
        )
        if open_loan_count > self.MAX_OPEN_LOANS:
            raise LoanLimitExceededError(
                f"a borrower cannot have more than {self.MAX_OPEN_LOANS} "
                "pending or active loans"
            )

        self._borrower_id = borrower_id
        self._role = role
        self._loans = restored_loans
        self._events: list[DomainEvent] = []

    @property
    def borrower_id(self) -> UUID:
        return self._borrower_id

    @property
    def role(self) -> BorrowerRole:
        return self._role

    @property
    def loans(self) -> tuple[Loan, ...]:
        return tuple(self._loans)

    def request_loan(
        self,
        projector_id: UUID,
        borrowing_period: BorrowingPeriod,
    ) -> UUID:
        if not isinstance(projector_id, UUID):
            raise TypeError("projector_id must be a UUID")
        if not isinstance(borrowing_period, BorrowingPeriod):
            raise TypeError("borrowing_period must be a BorrowingPeriod")
        if self.pending_and_active_count() >= self.MAX_OPEN_LOANS:
            raise LoanLimitExceededError(
                f"a borrower cannot have more than {self.MAX_OPEN_LOANS} "
                "pending or active loans"
            )

        loan = Loan(uuid4(), projector_id, borrowing_period)
        self._loans.append(loan)
        return loan.id

    def issue_loan(self, loan_id: UUID) -> None:
        loan = self._find_loan(loan_id)
        loan.mark_issued()
        self._events.append(
            LoanIssued(
                loan_id=loan.id,
                borrower_id=self.borrower_id,
                projector_id=loan.projector_id,
                due_date=loan.borrowing_period.due_date,
            )
        )

    def return_loan(self, loan_id: UUID) -> None:
        loan = self._find_loan(loan_id)
        loan.mark_returned()
        self._events.append(
            LoanReturned(
                loan_id=loan.id,
                borrower_id=self.borrower_id,
                projector_id=loan.projector_id,
            )
        )

    def cancel_loan(self, loan_id: UUID) -> None:
        self._find_loan(loan_id).mark_cancelled()

    def pending_and_active_count(self) -> int:
        open_statuses = {LoanStatus.PENDING, LoanStatus.ACTIVE}
        return sum(loan.status in open_statuses for loan in self._loans)

    def get_loan(self, loan_id: UUID) -> Loan:
        return self._find_loan(loan_id)

    def pull_events(self) -> list[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events

    def _find_loan(self, loan_id: UUID) -> Loan:
        if not isinstance(loan_id, UUID):
            raise TypeError("loan_id must be a UUID")
        for loan in self._loans:
            if loan.id == loan_id:
                return loan
        raise LoanNotFoundError(loan_id)

    def get_borrower_id(self) -> UUID:
        return self.borrower_id

    def get_role(self) -> BorrowerRole:
        return self.role

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Borrower):
            return NotImplemented
        return self.borrower_id == other.borrower_id

    def __hash__(self) -> int:
        return hash(self.borrower_id)

    def __repr__(self) -> str:
        return (
            f"Borrower(borrower_id={self.borrower_id!r}, "
            f"role={self.role!r})"
        )
