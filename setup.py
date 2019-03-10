#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2017-2019 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

import setuptools

setuptools.setup(
    name="git-autoshare",
    use_scm_version=True,
    description="A git clone wrapper that automatically uses --reference "
    "to save time and space.",
    long_description="\n".join((open("README.rst").read(), open("CHANGES.rst").read())),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: " "GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
    ],
    license="GPLv3",
    author="ACSONE SA/NV",
    author_email="info@acsone.eu",
    url="http://github.com/acsone/git-autoshare",
    packages=["git_autoshare"],
    install_requires=["appdirs", "click", "pyyaml"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    setup_requires=["setuptools-scm"],
    entry_points={
        "console_scripts": [
            "git-autoshare-clone=git_autoshare.clone:main",
            "git-autoshare-prefetch=git_autoshare.prefetch:main",
            "git-autoshare-submodule-add=git_autoshare.submodule:add",
        ]
    },
)
