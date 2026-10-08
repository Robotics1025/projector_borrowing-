from uuid import UUID

from .enums import ProjectorStatus, ProjectorType
from .exceptions import InvalidProjectorTransitionError


class Projector:
    def __init__(
        self,
        projector_id: UUID,
        projector_type: ProjectorType,
        status: ProjectorStatus = ProjectorStatus.AVAILABLE,
        version: int = 0,
    ) -> None:
        if not isinstance(projector_id, UUID):
            raise TypeError("projector_id must be a UUID")
        if not isinstance(projector_type, ProjectorType):
            raise TypeError("projector_type must be a ProjectorType")
        if not isinstance(status, ProjectorStatus):
            raise TypeError("status must be a ProjectorStatus")
        if not isinstance(version, int) or isinstance(version, bool):
            raise TypeError("version must be an integer")
        if version < 0:
            raise ValueError("version cannot be negative")

        self._projector_id = projector_id
        self._projector_type = projector_type
        self._status = status
        self._version = version

    @property
    def projector_id(self) -> UUID:
        return self._projector_id

    @property
    def projector_type(self) -> ProjectorType:
        return self._projector_type

    @property
    def status(self) -> ProjectorStatus:
        return self._status

    @property
    def version(self) -> int:
        return self._version

    def is_available(self) -> bool:
        return self.status is ProjectorStatus.AVAILABLE

    def mark_borrowed(self) -> None:
        if not self.is_available():
            raise InvalidProjectorTransitionError(
                "only available projectors can be marked as borrowed"
            )
        self._change_status(ProjectorStatus.BORROWED)

    def mark_available(self) -> None:
        if self.status not in {
            ProjectorStatus.BORROWED,
            ProjectorStatus.MAINTENANCE,
        }:
            raise InvalidProjectorTransitionError(
                "only borrowed projectors or projectors in maintenance "
                "can be marked as available"
            )
        self._change_status(ProjectorStatus.AVAILABLE)

    def mark_for_maintenance(self) -> None:
        if self.status is ProjectorStatus.BORROWED:
            raise InvalidProjectorTransitionError(
                "a borrowed projector cannot enter maintenance"
            )
        if self.status is ProjectorStatus.MAINTENANCE:
            raise InvalidProjectorTransitionError(
                "projector is already in maintenance"
            )
        self._change_status(ProjectorStatus.MAINTENANCE)

    def complete_maintenance(self) -> None:
        if self.status is not ProjectorStatus.MAINTENANCE:
            raise InvalidProjectorTransitionError(
                "only projectors in maintenance can become available"
            )
        self.mark_available()

    def _change_status(self, status: ProjectorStatus) -> None:
        self._status = status
        self._version += 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Projector):
            return NotImplemented
        return self.projector_id == other.projector_id

    def __hash__(self) -> int:
        return hash(self.projector_id)

    def __repr__(self) -> str:
        return (
            f"Projector(projector_id={self.projector_id!r}, "
            f"projector_type={self.projector_type!r}, "
            f"status={self.status!r}, version={self.version!r})"
        )
