from typing import Optional

from anyio import to_thread
from github import Github
from github.Label import Label
from github.Repository import Repository

from Shared.functions.readSettingsFile import get_setting

_REPO: Optional[Repository] = None
_LABELS: Optional[list[Label]] = None


async def get_github_repo() -> Optional[Repository]:
    """Returns the GitHub api repo object"""

    global _REPO

    if not _REPO:
        if get_setting("GITHUB_APPLICATION_API_KEY") and get_setting("GITHUB_REPOSITORY_ID"):
            github_api = Github(get_setting("GITHUB_APPLICATION_API_KEY"))

            # run those in a thread with anyio since they are blocking
            _REPO = await to_thread.run_sync(github_api.get_repo, get_setting("GITHUB_REPOSITORY_ID"))

    return _REPO


async def get_github_labels() -> Optional[list[Label]]:
    """Returns the GitHub labels that should be used on the issue"""

    global _LABELS

    if not _LABELS and get_setting("GITHUB_ISSUE_LABEL_NAMES"):
        repo = await get_github_repo()
        if repo:
            _LABELS = []
            for label_name in get_setting("GITHUB_ISSUE_LABEL_NAMES"):
                # run those in a thread with anyio since they are blocking
                label = await to_thread.run_sync(repo.get_label, label_name)

                _LABELS.append(label)

    return _LABELS
