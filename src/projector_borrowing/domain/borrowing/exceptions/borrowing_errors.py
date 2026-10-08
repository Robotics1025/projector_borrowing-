from uuid import UUID


class BorrowingDomainError(Exception):
    pass


class InvalidBorrowingPeriodError(BorrowingDomainError, ValueError):
    pass


class LoanLimitExceededError(BorrowingDomainError):
    pass


class LoanNotFoundError(BorrowingDomainError, LookupError):
    def __init__(self, loan_id: UUID) -> None:
        super().__init__(f"loan {loan_id} was not found")


class InvalidLoanTransitionError(BorrowingDomainError, ValueError):
    pass


class BorrowingEligibilityError(BorrowingDomainError):
    pass


class ProjectorUnavailableError(BorrowingEligibilityError):
    pass


class PremiumProjectorRestrictedError(BorrowingEligibilityError):
    pass
