""" """


class EnvError(Exception):
    pass


class InvalidPackagePath(EnvError):
    pass


class CondaEnvNotFound(EnvError):
    pass
