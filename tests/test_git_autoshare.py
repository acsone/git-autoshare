# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

import os
import subprocess

import pytest
import yaml

from git_autoshare.core import _repo_cached, git_bin


class Config:
    def __init__(self, tmpdir_factory):
        self.cache_dir = tmpdir_factory.mktemp("cache")
        self.config_dir = tmpdir_factory.mktemp("config")
        self.work_dir = tmpdir_factory.mktemp("work")
        self.repo_dir = tmpdir_factory.mktemp("repo")
        subprocess.call(["git", "init", str(self.repo_dir)])
        os.environ["GIT_AUTOSHARE_CACHE_DIR"] = str(self.cache_dir)
        os.environ["GIT_AUTOSHARE_CONFIG_DIR"] = str(self.config_dir)

    def write_repos_yml(self, d):
        with self.config_dir.join("repos.yml").open("w") as f:
            yaml.dump(d, f)


@pytest.fixture(scope="function")
def config(tmpdir_factory):
    return Config(tmpdir_factory)


def test_prefetch_all(config):
    config.write_repos_yml(
        {
            "github.com": {
                "mis-builder": {"orgs": ["OCA", "acsone"], "private": False},
                "git-aggregator": ["acsone"],
            }
        }
    )
    host_dir = config.cache_dir.join("github.com")
    subprocess.check_call(["git", "autoshare-prefetch"])
    assert host_dir.check(dir=1)
    assert host_dir.join("mis-builder").join("objects").check(dir=1)
    assert host_dir.join("git-aggregator").join("objects").check(dir=1)
    subprocess.check_call(["git", "autoshare-prefetch", "--quiet"])


def test_prefetch_one(config):
    config.write_repos_yml(
        {"github.com": {"mis-builder": ["OCA", "acsone"], "git-aggregator": ["acsone"]}}
    )
    host_dir = config.cache_dir.join("github.com")
    subprocess.check_call(
        ["git", "autoshare-prefetch", "https://github.com/acsone/git-aggregator.git"]
    )
    assert host_dir.check(dir=1)
    assert host_dir.join("git-aggregator").join("objects").check(dir=1)
    assert host_dir.join("mis-builder").check(exists=0)
    r = subprocess.call(
        ["git", "autoshare-prefetch", "https://github.com/acsone/notfound.git"]
    )
    assert r != 0


def test_clone_no_repos_yml(config):
    clone_dir = config.work_dir.join("git-aggregator")
    subprocess.check_call(
        [
            "git",
            "autoshare-clone",
            "https://github.com/acsone/git-aggregator.git",
            str(clone_dir),
        ]
    )
    assert clone_dir.join(".git").check(dir=1)
    assert (
        config.cache_dir.join("github.com")
        .join("git-aggregator")
        .join("objects")
        .check(exists=0)
    )


def test_clone(config):
    config.write_repos_yml(
        {"github.com": {"mis-builder": ["OCA", "acsone"], "git-aggregator": ["acsone"]}}
    )
    clone_dir = config.work_dir.join("git-aggregator")
    subprocess.check_call(
        [
            "git",
            "autoshare-clone",
            "https://github.com/acsone/git-aggregator.git",
            str(clone_dir),
        ]
    )
    alternates_file = (
        clone_dir.join(".git").join("objects").join("info").join("alternates")
    )
    cache_objects_dir = (
        config.cache_dir.join("github.com").join("git-aggregator").join("objects")
    )
    assert alternates_file.check(file=1)
    assert alternates_file.read().strip() == str(cache_objects_dir)
    assert cache_objects_dir.check(dir=1)


def test_clone_case_insensitive(config):
    config.write_repos_yml(
        {"github.com": {"Mis-Builder": ["OCA", "acsone"], "git-aggregator": ["acsone"]}}
    )
    clone_dir = config.work_dir.join("mis-builder")
    # clone with different case than config and missing .git suffix
    subprocess.check_call(
        ["git", "autoshare-clone", "https://GitHub.com/Oca/MIS-builder", str(clone_dir)]
    )
    alternates_file = (
        clone_dir.join(".git").join("objects").join("info").join("alternates")
    )
    # cache dir preserves case from config
    cache_objects_dir = (
        config.cache_dir.join("github.com").join("Mis-Builder").join("objects")
    )
    assert alternates_file.check(file=1)
    assert alternates_file.read().strip() == str(cache_objects_dir)
    assert cache_objects_dir.check(dir=1)


def test_submodule(config):
    config.write_repos_yml(
        {"github.com": {"mis-builder": ["OCA", "acsone"], "git-aggregator": ["acsone"]}}
    )
    local_path = "./git-aggregator"
    old_cwd = os.getcwd()
    # we need to cd into a repository for git submodule to work
    os.chdir(str(config.repo_dir))
    subprocess.check_call(
        [
            "git",
            "autoshare-submodule-add",
            "https://github.com/acsone/git-aggregator.git",
            local_path,
        ]
    )
    alternates_file = (
        config.repo_dir.join(".git")
        .join("modules")
        .join("git-aggregator")
        .join("objects")
        .join("info")
        .join("alternates")
    )
    cache_objects_dir = (
        config.cache_dir.join("github.com").join("git-aggregator").join("objects")
    )
    assert alternates_file.check(file=1)
    assert alternates_file.read().strip() == str(cache_objects_dir)
    assert cache_objects_dir.check(dir=1)
    # we return to the old place just in case
    os.chdir(old_cwd)


def test_repo_cached(config):
    config.write_repos_yml(
        {"github.com": {"mis-builder": ["OCA", "acsone"], "git-aggregator": ["acsone"]}}
    )
    cmd = [git_bin(), "clone", "https://github.com/acsone/git-aggregator.git"]
    found, index, kwargs = _repo_cached(cmd)
    assert found is True
    assert index == 2
    assert kwargs == {
        "host": "github.com",
        "orgs": ["acsone"],
        "private": False,
        "repo": "git-aggregator",
        "repo_dir": os.path.join(str(config.cache_dir), "github.com/git-aggregator"),
    }

    cmd = [git_bin(), "clone", "https://github.com/acsone/git-autoshare.git"]
    found, index, kwargs = _repo_cached(cmd)
    assert found is False
    assert index == 0
    assert kwargs == {}

    cmd = [
        git_bin(),
        "clone",
        "--verbose ",
        "https://github.com/acsone/git-autoshare.git",
    ]
    found, index, kwargs = _repo_cached(cmd)
    assert found is False
    assert index == 0
    assert kwargs == {}
