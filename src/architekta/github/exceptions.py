"""Exception hierarchy for GitHub operations."""


class GitHubError(Exception):
    pass


class RemoteNotFound(GitHubError):
    pass


class DescriptionNotFound(GitHubError):
    pass


class GhCliError(GitHubError):
    pass
