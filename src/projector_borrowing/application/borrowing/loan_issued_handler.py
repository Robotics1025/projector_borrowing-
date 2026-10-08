from ...domain.borrowing import LoanIssued
from ...domain.projectors import ProjectorRepository
from ._loaders import load_projector


class LoanIssuedHandler:
    def __init__(self, projector_repository: ProjectorRepository) -> None:
        self._projector_repository = projector_repository

    def handle(self, event: LoanIssued) -> None:
        projector = load_projector(
            self._projector_repository,
            event.projector_id,
        )
        expected_version = projector.version
        projector.mark_borrowed()
        self._projector_repository.save(
            projector,
            expected_version=expected_version,
        )
