# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import os
import subprocess

import appdirs
import yaml


APP_NAME = 'git-autoshare'


def cache_dir():
    return \
        os.environ.get('GIT_AUTOSHARE_CACHE_DIR') or \
        appdirs.user_cache_dir(APP_NAME)


def load_hosts():
    config_dir = \
        os.environ.get('GIT_AUTOSHARE_CONFIG_DIR') or \
        appdirs.user_config_dir(APP_NAME)
    repos_file = os.path.join(config_dir, 'repos.yml')
    if os.path.exists(repos_file):
        return yaml.load(open(repos_file))
    else:
        return {}


def git_bin():
    # TODO something more portable than /usr/bin/git
    return os.environ.get('GIT_AUTOSHARE_GIT_BIN') or '/usr/bin/git'


def repos():
    hosts = load_hosts()
    for host, repos in hosts.items():
        for repo, orgs in repos.items():
            repo_dir = os.path.join(cache_dir(), host, repo)
            orgs = [org.lower() for org in orgs]
            yield host, orgs, repo.lower(), repo_dir


def shared_urls():
    for host, orgs, repo, repo_dir in repos():
        for org in orgs:
            for suffix in ('', '.git'):
                repo_url = 'https://%s/%s/%s%s' % (host, org, repo, suffix)
                yield repo_url, host, org, repo, repo_dir
                repo_url = 'https://git@%s/%s/%s%s' % (host, org, repo, suffix)
                yield repo_url, host, org, repo, repo_dir
                repo_url = 'http://%s/%s/%s%s' % (host, org, repo, suffix)
                yield repo_url, host, org, repo, repo_dir
                repo_url = 'ssh://git@%s/%s/%s%s' % (host, org, repo, suffix)
                yield repo_url, host, org, repo, repo_dir
                repo_url = 'git@%s:%s/%s%s' % (host, org, repo, suffix)
                yield repo_url, host, org, repo, repo_dir


def prefetch_one(host, orgs, repo, repo_dir, quiet):
    if not os.path.exists(os.path.join(repo_dir, 'objects')):
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)
        subprocess.check_call([git_bin(), 'init', '--bare'], cwd=repo_dir)
    for org in orgs:
        try:
            subprocess.check_output([git_bin(), 'remote', 'remove', org],
                                    stderr=subprocess.STDOUT, cwd=repo_dir)
        except subprocess.CalledProcessError:
            pass
        repo_url = 'https://%s/%s/%s.git' % (host, org, repo)
        if not quiet:
            print("git-autoshare prefetching", repo_url, "in", repo_dir)
        subprocess.check_call([
            git_bin(), 'remote', 'add', org, repo_url], cwd=repo_dir)
    fetch_cmd = [git_bin(), 'fetch', '-f', '--all', '--tags']
    if quiet:
        fetch_cmd.append('-q')
    subprocess.check_call(fetch_cmd, cwd=repo_dir)


def prefetch_all(quiet):
    for host, orgs, repo, repo_dir in repos():
        prefetch_one(host, orgs, repo, repo_dir, quiet)
