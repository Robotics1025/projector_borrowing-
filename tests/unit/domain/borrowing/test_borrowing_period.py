from datetime import date, timedelta

import pytest

from projector_borrowing.domain.borrowing import (
    BorrowingPeriod,
    InvalidBorrowingPeriodError,
)


@pytest.mark.parametrize("duration", [1, 7])
def test_accepts_valid_duration(duration: int) -> None:
    start_date = date(2026, 10, 8)
    period = BorrowingPeriod(
        start_date,
        start_date + timedelta(days=duration),
    )
    assert period.duration_in_days() == duration


@pytest.mark.parametrize("duration", [-1, 0, 8])
def test_rejects_duration_outside_allowed_range(duration: int) -> None:
    start_date = date(2026, 10, 8)
    with pytest.raises(InvalidBorrowingPeriodError):
        BorrowingPeriod(
            start_date,
            start_date + timedelta(days=duration),
        )


def test_rejects_non_date_values() -> None:
    with pytest.raises(TypeError, match="start_date must be a date"):
        BorrowingPeriod("2026-10-08", date(2026, 10, 11))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="due_date must be a date"):
        BorrowingPeriod(date(2026, 10, 8), "2026-10-11")  # type: ignore[arg-type]
