# -*- coding: utf-8 -*-
# Copyright © 2017-2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import os
import subprocess

import appdirs
import giturlparse
import yaml

APP_NAME = "git-autoshare"


def cache_dir():
    return os.environ.get("GIT_AUTOSHARE_CACHE_DIR") or appdirs.user_cache_dir(APP_NAME)


_config = None


def config():
    global _config
    if _config is not None:
        return _config
    config_dir = os.environ.get("GIT_AUTOSHARE_CONFIG_DIR") or appdirs.user_config_dir(
        APP_NAME
    )
    repos_file = os.path.join(config_dir, "repos.yml")
    if os.path.exists(repos_file):
        with open(repos_file) as f:
            _config = yaml.load(f.read())
    else:
        print("git-autoshare ", repos_file, " not found. No hosts to load.")
        _config = {}
    return _config


def git_bin():
    # TODO something more portable than /usr/bin/git
    return os.environ.get("GIT_AUTOSHARE_GIT_BIN") or "/usr/bin/git"


def autoshare_repository(repository):
    giturl = giturlparse.parse(repository)
    if not giturl.valid:
        return None
    giturl_host = giturl.host.lower()
    giturl_repo = giturl.repo.lower()
    giturl_owner = giturl.owner.lower()
    for host, host_data in config().items():
        if host.lower() != giturl_host:
            continue
        for repo, repo_data in host_data.items():
            if repo.lower() != giturl_repo:
                continue
            if isinstance(repo_data, dict):
                orgs = repo.get("orgs", [])
                private = repo.get("private")
            else:
                orgs = repo_data
                private = False
            for org in orgs:
                if org.lower() != giturl_owner:
                    continue
                # match!
                return AutoshareRepository(host, [org], repo, private)
    return None


def find_autoshare_repository(args):
    for index, arg in enumerate(args):
        if arg.startswith("-"):
            continue
        ar = autoshare_repository(arg)
        if ar:
            return index, ar
    return -1, None


def autoshare_repositories():
    hosts = config()
    for host, repos in hosts.items():
        for repo, repo_data in repos.items():
            if isinstance(repo_data, dict):
                orgs = repo_data.get("orgs", [])
                private = repo_data.get("private", False)
            else:
                orgs = repo_data
                private = False
            yield AutoshareRepository(host, orgs, repo, private)


def git_remotes(repo_dir="."):
    remotes = subprocess.check_output(
        [git_bin(), "remote"], cwd=repo_dir, universal_newlines=True
    )
    for remote in remotes.split():
        url = subprocess.check_output(
            [git_bin(), "remote", "get-url", remote],
            cwd=repo_dir,
            universal_newlines=True,
        )
        yield remote, url.strip()


class AutoshareRepository:
    def __init__(self, host, orgs, repo, private):
        self.host = host
        self.orgs = orgs
        self.repo = repo
        self.private = private
        self.repo_dir = os.path.join(cache_dir(), self.host, self.repo)

    def setup_remotes(self, quiet):
        if not os.path.exists(os.path.join(self.repo_dir, "objects")):
            if not os.path.exists(self.repo_dir):
                os.makedirs(self.repo_dir)
            subprocess.check_call([git_bin(), "init", "--bare"], cwd=self.repo_dir)
        existing_remotes = dict(git_remotes(self.repo_dir))
        for org in self.orgs:
            if self.private:
                repo_url = "ssh://git@{}/{}/{}.git".format(self.host, org, self.repo)
            else:
                repo_url = "https://{}/{}/{}.git".format(self.host, org, self.repo)
            if org in existing_remotes:
                existing_repo_url = existing_remotes[org]
                if repo_url != existing_repo_url:
                    subprocess.check_call(
                        [git_bin(), "remote", "set-url", org, repo_url],
                        cwd=self.repo_dir,
                    )
                del existing_remotes[org]
            else:
                subprocess.check_call(
                    [git_bin(), "remote", "add", org, repo_url], cwd=self.repo_dir
                )
            if not quiet:
                print("git-autoshare remote", org, repo_url, "in", self.repo_dir)
        # remove remaining unneeded remotes
        for existing_remote in existing_remotes:
            if not quiet:
                print(
                    "git-autoshare removing remote",
                    existing_remote,
                    "in",
                    self.repo_dir,
                )
            subprocess.check_call(
                [git_bin(), "remote", "remove", existing_remote], cwd=self.repo_dir
            )

    def prefetch(self, quiet):
        self.setup_remotes(quiet)
        fetch_cmd = [git_bin(), "fetch", "-f", "--all", "--tags", "--prune"]
        if quiet:
            fetch_cmd.append("-q")
        subprocess.check_call(fetch_cmd, cwd=self.repo_dir)
