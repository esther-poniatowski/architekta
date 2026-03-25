"""Exception hierarchy for GitHub operations."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from architekta.infrastructure import CommandResult


class GitHubError(Exception):
    def __init__(self, message: str, *, diagnostics: "CommandResult | None" = None):
        super().__init__(message)
        self.diagnostics = diagnostics


class RemoteNotFound(GitHubError):
    pass


class DescriptionNotFound(GitHubError):
    pass


class GhCliError(GitHubError):
    pass


class MetadataParseError(GitHubError):
    pass
