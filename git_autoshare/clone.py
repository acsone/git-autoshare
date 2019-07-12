# -*- coding: utf-8 -*-
# Copyright © 2017-2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import subprocess
import sys

from .core import find_autoshare_repository, git_bin


def main():
    cmd = [git_bin(), "clone"] + sys.argv[1:]
    skip = any(
        c in cmd for c in ["--reference", "--reference-if-able", "-s", "--share"]
    )
    if not skip:
        quiet = "-q" in cmd or "--quiet" in cmd
        index, ar = find_autoshare_repository(cmd)
        if ar:
            ar.prefetch(quiet)
            if not quiet:
                print("git-autoshare clone added --reference", ar.repo_dir)
            cmd = cmd[:index] + ["--reference", ar.repo_dir] + cmd[index:]
    r = subprocess.call(cmd)
    sys.exit(r)
