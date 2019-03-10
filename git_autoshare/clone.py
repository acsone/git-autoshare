# -*- coding: utf-8 -*-
# Copyright © 2017-2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import os
import subprocess
import sys

from .core import _repo_cached, git_bin, prefetch_one


def main():
    cmd = [git_bin(), "clone"] + sys.argv[1:]
    skip = any(
        c in cmd for c in ["--reference", "--reference-if-able", "-s", "--share"]
    )
    if not skip:
        quiet = "-q" in cmd or "--quiet" in cmd
        found = False
        found, index, kwargs = _repo_cached(cmd)
        kwargs.update({"quiet": quiet})
        if found:
            if not os.path.exists(kwargs["repo_dir"]):
                prefetch_one(**kwargs)
            if not quiet:
                print("git-autoshare clone added --reference", kwargs["repo_dir"])
            cmd = cmd[:index] + ["--reference", kwargs["repo_dir"]] + cmd[index:]
    r = subprocess.call(cmd)
    sys.exit(r)
