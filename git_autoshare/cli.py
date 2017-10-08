# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

from __future__ import print_function

import os
import subprocess
import sys

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


def git_exe():
    # TODO a more portable way to do this
    return '/usr/bin/git'


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


def prefetch_one(host, orgs, repo, repo_dir):
    if not os.path.exists(os.path.join(repo_dir, 'objects')):
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)
        subprocess.check_call(['git', 'init', '--bare'], cwd=repo_dir)
    for org in orgs:
        try:
            subprocess.check_output(['git', 'remote', 'remove', org],
                                    stderr=subprocess.STDOUT, cwd=repo_dir)
        except subprocess.CalledProcessError:
            pass
        repo_url = 'https://%s/%s/%s.git' % (host, org, repo)
        subprocess.check_call(['git', 'remote', 'add', org, repo_url],
                              cwd=repo_dir)
    subprocess.check_call(['git', 'fetch', '-q', '-f', '--all', '--tags'],
                          cwd=repo_dir)


def prefetch_all():
    for host, orgs, repo, repo_dir in repos():
        prefetch_one(host, orgs, repo, repo_dir)


def main():
    if len(sys.argv) in (2, 3) and sys.argv[1] == 'prefetch':
        #
        # prefetch
        #
        if len(sys.argv) == 3:
            found = False
            for repo_url, host, org, repo, repo_dir in shared_urls():
                if sys.argv[2].lower() == repo_url:
                    prefetch_one(host, [org], repo, repo_dir)
                    found = True
                    break
            else:
                print(sys.argv[2], 'not found in repos.yml, not prefetched.')
                sys.exit(1)
        else:
            prefetch_all()
    else:
        #
        # clone --reference
        #
        cmd = [git_exe()] + sys.argv[1:]
        if len(sys.argv) > 1 and sys.argv[1] == 'clone':
            found = False
            for repo_url, host, org, repo, repo_dir in shared_urls():
                for i, arg in enumerate(sys.argv):
                    if arg.lower() == repo_url:
                        found = True
                        break
                if found:
                    break
            if found:
                print("git-autoshare", repo_dir)
                if not os.path.exists(repo_dir):
                    prefetch_one(host, [org], repo, repo_dir)
                cmd = cmd[:i] + ['--reference', repo_dir] + cmd[i:]
        r = subprocess.call(cmd)
        sys.exit(r)
