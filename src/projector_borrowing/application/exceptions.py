from uuid import UUID


class ApplicationError(Exception):
    pass


class ResourceNotFoundError(ApplicationError, LookupError):
    resource_name = "resource"

    def __init__(self, resource_id: UUID) -> None:
        self.resource_id = resource_id
        super().__init__(f"{self.resource_name} {resource_id} was not found")


class BorrowerNotFoundError(ResourceNotFoundError):
    resource_name = "borrower"


class ProjectorNotFoundError(ResourceNotFoundError):
    resource_name = "projector"
