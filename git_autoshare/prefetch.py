# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import sys

from .core import prefetch_all, prefetch_one, shared_urls


def main():
    exit = 0
    repositories = sys.argv[1:]
    if not repositories:
        prefetch_all()
    else:
        for repository in repositories:
            repository == repository.lower()
            for repo_url, host, org, repo, repo_dir in shared_urls():
                if repository == repo_url:
                    prefetch_one(host, [org], repo, repo_dir)
                    break
            else:
                print(repository, 'not found in repos.yml, not prefetched.')
                exit += 1
    sys.exit(exit)
