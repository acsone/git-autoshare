# Copyright © 2018 Camptocamp SA
# Copyright © 2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)


import subprocess
import sys
from pathlib import Path

from .core import find_autoshare_repository, git_bin


def iter_submodules(path=None):
    """Yield (path, url) for each submodule declared in .gitmodules file"""
    path = Path(path) if path else Path()
    gitmodules = path if path.is_file() else path / ".gitmodules"
    if not gitmodules.exists():
        return
    out = subprocess.check_output(
        [git_bin(), "config", "-f", str(gitmodules), "-l"]
    ).decode()
    submodules = {}
    for line in out.splitlines():
        key, _, value = line.partition("=")
        if not key.startswith("submodule."):
            continue
        name, _, field = key[len("submodule.") :].rpartition(".")
        if field in ("path", "url"):
            submodules.setdefault(name, {})[field] = value
    for sub in submodules.values():
        path, url = sub.get("path"), sub.get("url")
        if path and url:
            yield path, url


def update(repo_dir, path, url, quiet):
    """git submodule update --init <path> --reference <cache>"""
    cmd = [git_bin(), "submodule", "update", "--init"]
    if quiet:
        cmd.append("--quiet")
    _, ar = find_autoshare_repository([url])
    if ar:
        if not (Path(ar.repo_dir) / "objects").exists():
            ar.prefetch(quiet)
        cmd += ["--reference", ar.repo_dir]
    cmd.append(path)
    return subprocess.call(cmd, cwd=repo_dir)


def add():
    cmd = [git_bin(), "submodule", "add"] + sys.argv[1:]
    skip = "--reference" in cmd
    if not skip:
        quiet = "-q" in cmd or "--quiet" in cmd
        index, ar = find_autoshare_repository(cmd)
        if ar:
            if not Path(ar.repo_dir).exists():
                ar.prefetch(quiet)
            if not quiet:
                print("git-autoshare submodule-add added --reference", ar.repo_dir)
            cmd = cmd[:index] + ["--reference", ar.repo_dir] + cmd[index:]
    r = subprocess.call(cmd)
    sys.exit(r)
