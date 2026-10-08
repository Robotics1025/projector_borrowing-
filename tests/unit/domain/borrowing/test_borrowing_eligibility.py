from uuid import uuid4

import pytest

from projector_borrowing.domain.borrowing import (
    Borrower,
    BorrowingEligibilityService,
    BorrowingPeriod,
    LoanLimitExceededError,
    PremiumProjectorRestrictedError,
    ProjectorUnavailableError,
)
from projector_borrowing.domain.projectors import Projector


def test_allows_student_with_available_standard_projector(
    student_borrower: Borrower,
    standard_projector: Projector,
) -> None:
    BorrowingEligibilityService.check_eligibility(
        student_borrower,
        standard_projector,
    )


def test_allows_staff_with_available_premium_projector(
    staff_borrower: Borrower,
    premium_projector: Projector,
) -> None:
    BorrowingEligibilityService.check_eligibility(
        staff_borrower,
        premium_projector,
    )


def test_rejects_unavailable_projector(
    staff_borrower: Borrower,
    standard_projector: Projector,
) -> None:
    standard_projector.mark_borrowed()
    with pytest.raises(ProjectorUnavailableError):
        BorrowingEligibilityService.check_eligibility(
            staff_borrower,
            standard_projector,
        )


def test_rejects_premium_projector_for_student(
    student_borrower: Borrower,
    premium_projector: Projector,
) -> None:
    with pytest.raises(PremiumProjectorRestrictedError):
        BorrowingEligibilityService.check_eligibility(
            student_borrower,
            premium_projector,
        )


def test_rejects_borrower_at_open_loan_limit(
    staff_borrower: Borrower,
    standard_projector: Projector,
    borrowing_period: BorrowingPeriod,
) -> None:
    staff_borrower.request_loan(uuid4(), borrowing_period)
    staff_borrower.request_loan(uuid4(), borrowing_period)
    with pytest.raises(LoanLimitExceededError):
        BorrowingEligibilityService.check_eligibility(
            staff_borrower,
            standard_projector,
        )


def test_rejects_invalid_service_arguments(
    staff_borrower: Borrower,
    standard_projector: Projector,
) -> None:
    with pytest.raises(TypeError, match="borrower must be a Borrower"):
        BorrowingEligibilityService.check_eligibility(  # type: ignore[arg-type]
            object(),
            standard_projector,
        )
    with pytest.raises(TypeError, match="projector must be a Projector"):
        BorrowingEligibilityService.check_eligibility(  # type: ignore[arg-type]
            staff_borrower,
            object(),
        )
