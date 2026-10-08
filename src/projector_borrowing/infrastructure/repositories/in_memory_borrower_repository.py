from copy import deepcopy
from threading import RLock
from uuid import UUID

from ...domain.borrowing import Borrower


class InMemoryBorrowerRepository:
    def __init__(self, borrowers: tuple[Borrower, ...] = ()) -> None:
        self._lock = RLock()
        self._borrowers: dict[UUID, Borrower] = {}
        for borrower in borrowers:
            self.save(borrower)

    def get_by_id(self, borrower_id: UUID) -> Borrower | None:
        with self._lock:
            borrower = self._borrowers.get(borrower_id)
            return deepcopy(borrower) if borrower is not None else None

    def save(self, borrower: Borrower) -> None:
        if not isinstance(borrower, Borrower):
            raise TypeError("borrower must be a Borrower")
        with self._lock:
            self._borrowers[borrower.borrower_id] = deepcopy(borrower)
