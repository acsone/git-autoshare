# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import sys

import click

from .core import prefetch_all, prefetch_one, shared_urls


@click.command()
@click.option('--quiet', '-q', is_flag=True, default=False)
@click.argument('repositories', metavar='<repository> ...', nargs=-1)
def main(repositories, quiet):
    exit = 0
    if not repositories:
        prefetch_all(quiet)
    else:
        for repository in repositories:
            repository == repository.lower()
            for repo_url, host, org, repo, repo_dir in shared_urls():
                if repository == repo_url:
                    prefetch_one(host, [org], repo, repo_dir, quiet)
                    break
            else:
                print(repository, 'not found in repos.yml, not prefetched.')
                exit += 1
    sys.exit(exit)
