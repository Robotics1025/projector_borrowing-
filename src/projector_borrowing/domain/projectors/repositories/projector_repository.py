from typing import Protocol, runtime_checkable
from uuid import UUID

from ..projector import Projector


@runtime_checkable
class ProjectorRepository(Protocol):
    def get_by_id(self, projector_id: UUID) -> Projector | None:
        ...  # pragma: no cover

    def save(
        self,
        projector: Projector,
        *,
        expected_version: int | None = None,
    ) -> None:
        ...  # pragma: no cover
