"""Exception hierarchy for registry operations."""


class RegistryError(Exception):
    pass


class RegistryNotFound(RegistryError):
    pass


class InvalidRegistry(RegistryError):
    pass


class ProjectNotFound(RegistryError):
    pass
