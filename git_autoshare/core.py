# -*- coding: utf-8 -*-
# Copyright © 2017-2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import os
import shutil
import subprocess

import appdirs
import yaml

from . import giturlparse

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
            _config = yaml.safe_load(f.read())
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
                if repo == "*":
                    repo = giturl_repo
                else:
                    continue
            if isinstance(repo_data, dict):
                orgs = repo_data.get("orgs", [])
                private = repo_data.get("private")
            else:
                orgs = repo_data
                private = False

            valid_orgs = []
            for org in orgs:
                if org.lower() != giturl_owner:
                    continue
                valid_orgs.append(org)
            if valid_orgs:
                # match!
                return AutoshareRepository(host, valid_orgs, repo, private)
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
            if repo == "*":
                # TODO list cache directory? in which case the
                # TODO orgs to fetch must be take from refs/git-autoshare/*
                # TODO because a repo may not exist in all remotes
                continue
            if isinstance(repo_data, dict):
                orgs = repo_data.get("orgs", [])
                private = repo_data.get("private", False)
            else:
                orgs = repo_data
                private = False

            yield AutoshareRepository(host, orgs, repo, private)

class AutoshareRepository:
    def __init__(self, host, orgs, repo, private):
        self.host = host
        self.orgs = orgs
        self.repo = repo
        self.private = private
        self.repo_dir = os.path.join(cache_dir(), self.host, self.repo)

    def prefetch(self, quiet):
        new_repo_dir = False
        if not os.path.exists(os.path.join(self.repo_dir, "objects")):
            new_repo_dir = True
            if not os.path.exists(self.repo_dir):
                os.makedirs(self.repo_dir)
            subprocess.check_call([git_bin(), "init", "--bare"], cwd=self.repo_dir)

        for org in self.orgs:
            if self.private:
                repo_url = "ssh://git@{host}/{org}/{repo}.git".format(
                    host=self.host, org=org, repo=self.repo
                )
            else:
                repo_url = "https://{host}/{org}/{repo}.git".format(
                    host=self.host, org=org, repo=self.repo
                )
            fetch_cmd = [git_bin(), "fetch", "--force"]
            if quiet:
                fetch_cmd.append("-q")
            fetch_cmd.append(repo_url)
            fetch_cmd.append(
                "refs/heads/*:refs/git-autoshare/{org}/heads/*".format(org=org)
            )
            try:
                subprocess.check_call(fetch_cmd, cwd=self.repo_dir)
            except Exception:
                if new_repo_dir:
                    shutil.rmtree(self.repo_dir)
                raise
