# -*- coding: utf-8 -*-
# Copyright © 2017-2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import sys

import click

from .core import autoshare_repositories, autoshare_repository


@click.command()
@click.option("--quiet", "-q", is_flag=True, default=False)
@click.argument("repositories", metavar="<repository> ...", nargs=-1)
def main(repositories, quiet):
    exit = 0
    if not repositories:
        for ar in autoshare_repositories():
            ar.prefetch(quiet)
    else:
        for repository in repositories:
            ar = autoshare_repository(repository)
            if ar:
                ar.prefetch(quiet)
            else:
                print(repository, "not found in repos.yml, not prefetched.")
                exit += 1
    sys.exit(exit)
