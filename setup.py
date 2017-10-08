#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

import setuptools

setuptools.setup(
    name='git-autoshare',
    use_scm_version=True,
    description='A git clone wrapper that automatically uses --reference.',
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    )),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
    ],
    license='GPLv3',
    author='ACSONE SA/NV',
    author_email='info@acsone.eu',
    url='http://github.com/acsone/git-autoshare',
    packages=[
        'git_autoshare',
    ],
    install_requires=[
        'appdirs',
        'pyyaml',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    test_suite='tests',
    entry_points={
        'console_scripts': [
            "git-autoshare=git_autoshare.cli:main",
            "git=git_autoshare.cli:main",
        ],
    },
)
