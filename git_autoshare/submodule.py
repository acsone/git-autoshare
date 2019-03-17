# -*- coding: utf-8 -*-
# Copyright © 2018 Camptocamp SA
# Copyright © 2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import os
import subprocess
import sys

from .core import find_autoshare_repository, git_bin


def add():
    cmd = [git_bin(), "submodule", "add"] + sys.argv[1:]
    skip = "--reference" in cmd
    if not skip:
        quiet = "-q" in cmd or "--quiet" in cmd
        index, ar = find_autoshare_repository(cmd)
        if ar:
            if not os.path.exists(ar.repo_dir):
                ar.prefetch(quiet)
            if not quiet:
                print("git-autoshare submodule-add added --reference", ar.repo_dir)
            cmd = cmd[:index] + ["--reference", ar.repo_dir] + cmd[index:]
    r = subprocess.call(cmd)
    sys.exit(r)
