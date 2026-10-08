from uuid import UUID

from ...domain.borrowing import Borrower, BorrowerRepository
from ...domain.projectors import Projector, ProjectorRepository
from ..exceptions import BorrowerNotFoundError, ProjectorNotFoundError


def load_borrower(
    repository: BorrowerRepository,
    borrower_id: UUID,
) -> Borrower:
    borrower = repository.get_by_id(borrower_id)
    if borrower is None:
        raise BorrowerNotFoundError(borrower_id)
    return borrower


def load_projector(
    repository: ProjectorRepository,
    projector_id: UUID,
) -> Projector:
    projector = repository.get_by_id(projector_id)
    if projector is None:
        raise ProjectorNotFoundError(projector_id)
    return projector
