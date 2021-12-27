from typing import Optional

from github import Github
from github.GithubObject import NotSet
from github.Label import Label
from github.Repository import Repository

from rename_to_settings import (
    GITHUB_APPLICATION_API_KEY,
    GITHUB_ISSUE_LABEL_NAMES,
    GITHUB_REPOSITORY_ID,
)

_REPO: Optional[Repository] = None
_LABELS: list[Label] | NotSet = NotSet


def get_github_repo() -> Optional[Repository]:
    """Returns the GitHub api repo object"""

    global _REPO

    if not _REPO:
        if GITHUB_APPLICATION_API_KEY and GITHUB_REPOSITORY_ID:
            github_api = Github(GITHUB_APPLICATION_API_KEY)
            _REPO = github_api.get_repo(GITHUB_REPOSITORY_ID)

    return _REPO


def get_github_labels() -> Optional[list[Label]]:
    """Returns the GitHub labels that should be used on the issue"""

    global _LABELS

    if _LABELS == NotSet and GITHUB_ISSUE_LABEL_NAMES:
        repo = get_github_repo()
        if repo:
            _LABELS = []
            for label_name in GITHUB_ISSUE_LABEL_NAMES:
                _LABELS.append(repo.get_label(label_name))

    return _LABELS
