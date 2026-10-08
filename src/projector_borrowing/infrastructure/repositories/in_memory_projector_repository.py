from copy import deepcopy
from threading import RLock
from uuid import UUID

from ...domain.projectors import Projector, ProjectorConcurrencyError


class InMemoryProjectorRepository:
    def __init__(self, projectors: tuple[Projector, ...] = ()) -> None:
        self._lock = RLock()
        self._projectors: dict[UUID, Projector] = {}
        for projector in projectors:
            self.save(projector)

    def get_by_id(self, projector_id: UUID) -> Projector | None:
        with self._lock:
            projector = self._projectors.get(projector_id)
            return deepcopy(projector) if projector is not None else None

    def save(
        self,
        projector: Projector,
        *,
        expected_version: int | None = None,
    ) -> None:
        if not isinstance(projector, Projector):
            raise TypeError("projector must be a Projector")
        if expected_version is not None and (
            not isinstance(expected_version, int)
            or isinstance(expected_version, bool)
            or expected_version < 0
        ):
            raise ValueError("expected_version must be a non-negative integer")

        with self._lock:
            current = self._projectors.get(projector.projector_id)
            if current is not None and expected_version != current.version:
                raise ProjectorConcurrencyError(
                    f"projector {projector.projector_id} version conflict: "
                    f"expected {expected_version}, current {current.version}"
                )
            self._projectors[projector.projector_id] = deepcopy(projector)
