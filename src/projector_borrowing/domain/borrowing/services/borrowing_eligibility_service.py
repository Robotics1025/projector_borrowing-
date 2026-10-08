from ...projectors import Projector, ProjectorType
from ..borrower import Borrower
from ..enums import BorrowerRole
from ..exceptions import (
    LoanLimitExceededError,
    PremiumProjectorRestrictedError,
    ProjectorUnavailableError,
)


class BorrowingEligibilityService:
    @staticmethod
    def check_eligibility(
        borrower: Borrower,
        projector: Projector,
        *,
        enforce_loan_limit: bool = True,
    ) -> None:
        if not isinstance(borrower, Borrower):
            raise TypeError("borrower must be a Borrower")
        if not isinstance(projector, Projector):
            raise TypeError("projector must be a Projector")
        if not projector.is_available():
            raise ProjectorUnavailableError(
                "only available projectors can be borrowed"
            )
        if (
            enforce_loan_limit
            and borrower.pending_and_active_count() >= borrower.MAX_OPEN_LOANS
        ):
            raise LoanLimitExceededError(
                f"a borrower cannot have more than {borrower.MAX_OPEN_LOANS} "
                "pending or active loans"
            )
        if (
            borrower.role is BorrowerRole.STUDENT
            and projector.projector_type is ProjectorType.PREMIUM
        ):
            raise PremiumProjectorRestrictedError(
                "students cannot borrow premium projectors"
            )
