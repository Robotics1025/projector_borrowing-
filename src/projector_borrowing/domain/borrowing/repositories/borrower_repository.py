from typing import Protocol, runtime_checkable
from uuid import UUID

from ..borrower import Borrower


@runtime_checkable
class BorrowerRepository(Protocol):
    def get_by_id(self, borrower_id: UUID) -> Borrower | None:
        ...  # pragma: no cover

    def save(self, borrower: Borrower) -> None:
        ...  # pragma: no cover
