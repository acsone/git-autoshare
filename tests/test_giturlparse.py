import pytest

from git_autoshare.giturlparse import GitUrl, InvalidGitUrl, parse

valid_giturl = GitUrl("github.com", "owner", "repo")
testdata = [
    ("ssh://git@github.com/owner/repo.git", valid_giturl),
    ("https://git@github.com/owner/repo.git", valid_giturl),
    ("git://git@github.com/owner/repo.git", valid_giturl),
    ("ssh://github.com/owner/repo.git", valid_giturl),
    ("https://github.com/owner/repo.git", valid_giturl),
    ("git://github.com/owner/repo.git", valid_giturl),
    ("ssh://github.com/owner/repo", valid_giturl),
    ("https://github.com/owner/repo", valid_giturl),
    ("git://github.com/owner/repo", valid_giturl),
    ("git@github.com:owner/repo", valid_giturl),
    ("randomstuff", InvalidGitUrl()),
]


@pytest.mark.parametrize("url, expected_giturl", testdata)
def test_giturlparse(url, expected_giturl):
    giturl = parse(url)
    assert giturl.valid == expected_giturl.valid
    assert giturl.host == expected_giturl.host
    assert giturl.owner == expected_giturl.owner
    assert giturl.repo == expected_giturl.repo
