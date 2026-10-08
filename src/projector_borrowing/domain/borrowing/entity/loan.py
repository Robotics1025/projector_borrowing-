from uuid import UUID

from ..enums import LoanStatus
from ..exceptions import InvalidLoanTransitionError
from ..valueobject import BorrowingPeriod


class Loan:
    def __init__(
        self,
        loan_id: UUID,
        projector_id: UUID,
        borrowing_period: BorrowingPeriod,
        status: LoanStatus = LoanStatus.PENDING,
    ) -> None:
        if not isinstance(loan_id, UUID):
            raise TypeError("loan_id must be a UUID")
        if not isinstance(projector_id, UUID):
            raise TypeError("projector_id must be a UUID")
        if not isinstance(borrowing_period, BorrowingPeriod):
            raise TypeError("borrowing_period must be a BorrowingPeriod")
        if not isinstance(status, LoanStatus):
            raise TypeError("status must be a LoanStatus")

        self._id = loan_id
        self._projector_id = projector_id
        self._borrowing_period = borrowing_period
        self._status = status

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def projector_id(self) -> UUID:
        return self._projector_id

    @property
    def status(self) -> LoanStatus:
        return self._status

    @property
    def borrowing_period(self) -> BorrowingPeriod:
        return self._borrowing_period

    def mark_issued(self) -> None:
        if self._status != LoanStatus.PENDING:
            raise InvalidLoanTransitionError(
                "only pending loans can be issued"
            )

        self._status = LoanStatus.ACTIVE

    def mark_returned(self) -> None:
        if self._status != LoanStatus.ACTIVE:
            raise InvalidLoanTransitionError(
                "only active loans can be returned"
            )

        self._status = LoanStatus.RETURNED

    def mark_cancelled(self) -> None:
        if self._status != LoanStatus.PENDING:
            raise InvalidLoanTransitionError(
                "only pending loans can be cancelled"
            )

        self._status = LoanStatus.CANCELLED

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Loan):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"Loan(id={self.id!r}, projector_id={self.projector_id!r}, "
            f"borrowing_period={self.borrowing_period!r}, "
            f"status={self.status!r})"
        )
