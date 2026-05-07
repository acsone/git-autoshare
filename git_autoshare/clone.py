# Copyright © 2017-2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)


import subprocess
import sys

from .core import find_autoshare_repository, git_bin
from .submodule import iter_submodules
from .submodule import update as submodule_update


def main():
    args = sys.argv[1:]
    recurse = "--recurse-submodules" in args or "--recursive" in args
    args = [a for a in args if a not in ("--recurse-submodules", "--recursive")]

    cmd = [git_bin(), "clone"] + args
    skip = any(
        c in cmd for c in ["--reference", "--reference-if-able", "-s", "--share"]
    )
    quiet = "-q" in cmd or "--quiet" in cmd
    if not skip:
        index, ar = find_autoshare_repository(cmd)
        if ar:
            ar.prefetch(quiet)
            if not quiet:
                print("git-autoshare clone added --reference", ar.repo_dir)
            cmd = cmd[:index] + ["--reference", ar.repo_dir] + cmd[index:]
    r = subprocess.call(cmd)
    if r != 0 or not recurse:
        sys.exit(r)

    target, _explicit_target = get_clone_target_dir_from_args(args)
    sys.exit(_init_submodules(target, quiet))


def _init_submodules(target, quiet):
    for path, url in iter_submodules(target):
        r = submodule_update(target, path, url, quiet)
        if r != 0:
            return r
    return 0


def get_clone_target_dir_from_args(args):
    """Returns the target directory of the clone, and whether it was explicitly"""
    positionals = [a for a in args if not a.startswith("-")]
    # Check if we provided an explicity destination
    if len(positionals) >= 2:
        return positionals[-1], True
    # Extract from the repo URL
    name = positionals[0].rstrip("/").rsplit("/", 1)[-1]
    dest = name[:-4] if name.endswith(".git") else name
    return dest, False
