class ProjectorDomainError(Exception):
    pass


class InvalidProjectorTransitionError(ProjectorDomainError, ValueError):
    pass


class ProjectorConcurrencyError(ProjectorDomainError):
    pass
