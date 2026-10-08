from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from uuid import UUID


@dataclass(frozen=True, slots=True)
class LoanIssued:
    loan_id: UUID
    borrower_id: UUID
    projector_id: UUID
    due_date: date
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
