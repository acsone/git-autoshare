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
    test_mode = os.environ["GIT_AUTOSHARE_MODE"] == "test"
    if not test_mode and _config is not None:
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


def _get_all_declared_repos(host):
    """Get all declared repos from config for a single host"""
    return set(config()[host].keys()).difference(["*"])


def _get_cached_and_undeclared_repositories(host):
    """Returns only cached repositories and undeclared in configuration"""
    cached_repos = set()
    host_dir = os.path.join(cache_dir(), host)
    # If folder doesn't exist, autoshare-clone or submodules were not used yet
    if os.path.isdir(host_dir):
        cached_repos = set(os.listdir(host_dir))  # From cache only
        declared_repos = _get_all_declared_repos(host)  # From repos only
        # Return the difference
        return cached_repos.difference(declared_repos)
    return cached_repos


def find_wildcarded_repositories(host, orgs, private):
    """Find undeclared repositories from a single wildcard configuration"""
    for repo in _get_cached_and_undeclared_repositories(host):
        print("Found a cached repository '{}'".format(repo))
        orgs_path = os.path.join(cache_dir(), host, repo, "refs", "git-autoshare")
        # If a cached org's folder doesn't exist, clone has not been called yet
        # We don't process it
        # And lowercase is used to avoid differences by false negative
        if os.path.exists(orgs_path):
            existing_orgs = [o.lower() for o in os.listdir(orgs_path)]
            # But we keep the original org value for further process
            valid_orgs = [org for org in orgs if org.lower() in existing_orgs]
            if valid_orgs:
                print("Processing '{}' for orgs {}".format(repo, valid_orgs))
                yield AutoshareRepository(host, valid_orgs, repo, private)


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

            if repo == "*":
                print(
                    "Global prefetch started for host {} and orgs {}...".format(
                        host, orgs
                    )
                )
                for ar in find_wildcarded_repositories(host, orgs, private):
                    yield ar
            else:
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
                print("Prefetching {}/{}/{}".format(self.host, org, self.repo))
                subprocess.check_call(fetch_cmd, cwd=self.repo_dir)
            except Exception:
                if new_repo_dir:
                    shutil.rmtree(self.repo_dir)
                raise

    def __hash__(self):
        return hash(self.repo_dir + str(self.private) + str(self.orgs))

    def __eq__(self, other):
        if isinstance(other, AutoshareRepository):
            return (
                self.repo_dir == other.repo_dir
                and self.orgs == other.orgs
                and self.private == other.private
            )
        return False
