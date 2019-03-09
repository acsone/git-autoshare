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
        print("git-autoshare ", repos_file, " not found. No hosts to load.")
        return {}


def git_bin():
    # TODO something more portable than /usr/bin/git
    return os.environ.get('GIT_AUTOSHARE_GIT_BIN') or '/usr/bin/git'


def repos():
    hosts = load_hosts()
    for host, repos in hosts.items():
        for repo, repo_data in repos.items():
            if isinstance(repo_data, dict):
                orgs = repo_data.get('orgs', [])
                private = repo_data.get('private', False)
            else:
                orgs = repo_data
                private = False
            repo_dir = os.path.join(cache_dir(), host, repo)
            orgs = [org.lower() for org in orgs]
            yield host, orgs, repo.lower(), repo_dir, private


def shared_urls():
    for host, orgs, repo, repo_dir, private in repos():
        for org in orgs:
            for suffix in ('', '.git'):
                if not private:
                    repo_url = 'https://%s/%s/%s%s' % \
                        (host, org, repo, suffix)
                    yield repo_url, host, org, repo, repo_dir, private
                    repo_url = 'https://git@%s/%s/%s%s' % \
                        (host, org, repo, suffix)
                    yield repo_url, host, org, repo, repo_dir, private
                    repo_url = 'http://%s/%s/%s%s' % \
                        (host, org, repo, suffix)
                    yield repo_url, host, org, repo, repo_dir, private
                repo_url = 'ssh://git@%s/%s/%s%s' % \
                    (host, org, repo, suffix)
                yield repo_url, host, org, repo, repo_dir, private
                repo_url = 'git@%s:%s/%s%s' % \
                    (host, org, repo, suffix)
                yield repo_url, host, org, repo, repo_dir, private


def _repo_cached(cmd):
    found = False
    for repo_url, host, org, repo, repo_dir, private in shared_urls():
        for index, arg in enumerate(cmd):
            if arg.startswith('-'):
                continue
            if arg.lower() == repo_url:
                found = True
                break
        if found:
            break
    if found:
        return found, index, {
            'host': host,
            'orgs': [org],
            'repo': repo,
            'repo_dir': repo_dir,
            'private': private,
        }
    else:
        return False, 0, {}


def git_remotes(repo_dir='.'):
    remotes = subprocess.check_output([git_bin(), 'remote'],
                                      cwd=repo_dir, universal_newlines=True)
    for remote in remotes.split():
        url = subprocess.check_output([git_bin(), 'remote', 'get-url', remote],
                                      cwd=repo_dir, universal_newlines=True)
        yield remote, url.strip()


def prefetch_one(host, orgs, repo, repo_dir, private, quiet):
    if not os.path.exists(os.path.join(repo_dir, 'objects')):
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)
        subprocess.check_call([git_bin(), 'init', '--bare'], cwd=repo_dir)
    existing_remotes = dict(git_remotes(repo_dir))
    for org in orgs:
        if private:
            repo_url = 'ssh://git@%s/%s/%s.git' % (host, org, repo)
        else:
            repo_url = 'https://%s/%s/%s.git' % (host, org, repo)
        if org in existing_remotes:
            existing_repo_url = existing_remotes[org]
            if repo_url != existing_repo_url:
                subprocess.check_call([
                    git_bin(), 'remote', 'set-url', org, repo_url],
                    cwd=repo_dir)
            del existing_remotes[org]
        else:
            subprocess.check_call([
                git_bin(), 'remote', 'add', org, repo_url],
                cwd=repo_dir)
        if not quiet:
            print("git-autoshare remote", org, repo_url, "in", repo_dir)
    # remove remaining unneeded remotes
    for existing_remote in existing_remotes:
        if not quiet:
            print("git-autoshare removing remote", existing_remote,
                  "in", repo_dir)
        subprocess.check_call([
            git_bin(), 'remote', 'remove', existing_remote],
            cwd=repo_dir)
    fetch_cmd = [git_bin(), 'fetch', '-f', '--all', '--tags', '--prune']
    if quiet:
        fetch_cmd.append('-q')
    subprocess.check_call(fetch_cmd, cwd=repo_dir)


def prefetch_all(quiet):
    for host, orgs, repo, repo_dir, private in repos():
        prefetch_one(host, orgs, repo, repo_dir, private, quiet)
