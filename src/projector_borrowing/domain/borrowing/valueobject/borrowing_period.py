from dataclasses import dataclass
from datetime import date

from ..exceptions import InvalidBorrowingPeriodError


@dataclass(frozen=True, slots=True)
class BorrowingPeriod:
    start_date: date
    due_date: date

    def __post_init__(self) -> None:
        if not isinstance(self.start_date, date):
            raise TypeError("start_date must be a date")
        if not isinstance(self.due_date, date):
            raise TypeError("due_date must be a date")
        if not 1 <= self.duration_in_days() <= 7:
            raise InvalidBorrowingPeriodError(
                "borrowing duration must be between 1 and 7 calendar days"
            )

    def duration_in_days(self) -> int:
        return (self.due_date - self.start_date).days
