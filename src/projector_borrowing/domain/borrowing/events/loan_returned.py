from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


@dataclass(frozen=True, slots=True)
class LoanReturned:
    loan_id: UUID
    borrower_id: UUID
    projector_id: UUID
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
