# -*- coding: utf-8 -*-
# Copyright © 2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

import re

_regexps = [
    re.compile(r)
    for r in [
        (
            r"^(http|https|ssh|git)://((?P<user>[^@]+)@)?(?P<host>[^/]+)/"
            r"(?P<owner>[^/]+)/(?P<repo>[^/]+?)(\.git)?$"
        ),
        (
            r"^((?P<user>[^@]+)@)?(?P<host>[^:]+):"
            r"(?P<owner>[^/]+)/(?P<repo>[^/]+?)(\.git)?$"
        ),
    ]
]


class GitUrlBase(object):
    __slots__ = ["valid", "host", "owner", "repo"]

    def __init__(self, valid, host, owner, repo):
        self.valid = valid
        self.host = host
        self.owner = owner
        self.repo = repo


class GitUrl(GitUrlBase):
    __slots__ = []

    def __init__(self, host, owner, repo):
        super(GitUrl, self).__init__(True, host, owner, repo)


class InvalidGitUrl(GitUrlBase):
    __slots__ = []

    def __init__(self):
        super(InvalidGitUrl, self).__init__(False, None, None, None)


def parse(url):
    for regexp in _regexps:
        mo = regexp.match(url)
        if mo:
            return GitUrl(mo.group("host"), mo.group("owner"), mo.group("repo"))
    return InvalidGitUrl()
