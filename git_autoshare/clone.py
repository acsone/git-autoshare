# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import os
import subprocess
import sys

from .core import git_bin, prefetch_one, shared_urls


def main():
    cmd = [git_bin(), 'clone'] + sys.argv[1:]
    skip = \
        '--reference' in cmd or \
        '--reference-if-able' in cmd or \
        '-s' in cmd or \
        '--share' in cmd
    if not skip:
        quiet = '-q' in cmd or '--quiet' in cmd
        found = False
        for repo_url, host, org, repo, repo_dir in shared_urls():
            for i, arg in enumerate(cmd):
                if arg.lower() == repo_url:
                    found = True
                    break
            if found:
                break
        if found:
            if not os.path.exists(repo_dir):
                prefetch_one(host, [org], repo, repo_dir, quiet)
            if not quiet:
                print("git-autoshare clone added --reference", repo_dir)
            cmd = cmd[:i] + ['--reference', repo_dir] + cmd[i:]
    r = subprocess.call(cmd)
    sys.exit(r)
