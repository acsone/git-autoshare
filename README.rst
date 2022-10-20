git-autoshare
=============

.. image:: https://img.shields.io/badge/license-GPL--3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0-standalone.html
   :alt: License: GPL-3
.. image:: https://badge.fury.io/py/git-autoshare.svg
    :target: http://badge.fury.io/py/git-autoshare
.. image:: https://results.pre-commit.ci/badge/github/acsone/git-autoshare/master.svg
   :target: https://results.pre-commit.ci/latest/github/acsone/git-autoshare/master
   :alt: pre-commit.ci status
.. image:: https://github.com/acsone/git-autoshare/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/acsone/git-autoshare/actions/workflows/ci.yml
   :alt: ci status
.. image:: https://codecov.io/gh/acsone/git-autoshare/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/acsone/git-autoshare

A git clone wrapper that automatically uses `--reference
<https://git-scm.com/docs/git-clone#git-clone---reference-if-ableltrepositorygt>`_
to save disk space and download time.

.. contents::

Installation
~~~~~~~~~~~~

To install git-autoshare in a fancy way, we recommend using `pipx <https://pypi.org/project/pipx-app/>`_.

After installing ``pipx`` simply run::

    $ pipx install git-autoshare

To upgrade git-autoshare at any time::

    $ pipx upgrade git-autoshare

This will also install a simple script to transparently replace your calls to ``git clone`` with calls to
``git autoshare-clone``. To enable it, export `GIT_AUTOSHARE=1` in your shell.

Usage
~~~~~

Configuration file
------------------

To configure it, create a file named ``git-autoshare/repos.yml`` in your user configuration
directory (often ``~/.config`` on Linux). This file must have the following structre::

    host:
        repo:
            orgs:
                - organization
                - ...
            private: (True|False)
        ...:
    ...:

It lists all git hosts, repositories, and organizations that are subject to the sharing
of git objects. Here is an example::

    github.com:
        odoo:
            orgs:
                - odoo
                - OCA
        enterprise:
            orgs:
                - odoo
                - acsone
            private: True
        mis-builder:
            # shortcut to provides organizations
            - OCA
            - acsone

Note the use of the ``private`` option, used to force fetching using the ssh protocol.

It is also possible to use ``*`` as a wildcard for repository name, to have
autoshare applied to all repos of some organizations::

    github.com:
        "*":
            orgs:
                - odoo
                - OCA
                - acsone
            private: True


git autoshare-clone command
---------------------------

If configured like the example above, when you git clone the odoo or mis-builder repositories
from one of these github organizations, ``git autoshare-clone`` will automatically insert the
``--reference`` option in the git clone command. For example::

    $ git autoshare-clone https://github.com/odoo/odoo

will be transformed into::

    $ /usr/bin/git clone --reference ~/.cache/git-autoshare/github.com/odoo https://github.com/odoo/odoo


git autoshare-submodule-add command
-----------------------------------

Same as ``git autoshare-clone`` command, you can add submodules with a
reference. for example::

    $ git autoshare-submodule-add https://github.com/odoo/odoo ./odoo

will be transformed into::

    $ /usr/bin/git submodule add --reference ~/.cache/git-autoshare/github.com/odoo https://github.com/odoo/odoo ./odoo


git autoshare-prefetch command
------------------------------

The ``autoshare-prefetch`` command is mostly meant to be run in a cron job::

    $ git autoshare-prefetch --quiet

will update the cache directory by fetching all repositories mentioned in repos.yml.

It can also prefetch one single repository, for example::

    $ git autoshare-prefetch https://github.com/odoo/odoo.git

Environment variables
---------------------

The cache directory is named ``git-autoshare`` where `appdirs <https://pypi.python.org/pypi/appdirs>`_.user_cache_dir is
(usually ~/.cache/git-autoshare/).
This location can be configured with the ``GIT_AUTOSHARE_CACHE_DIR`` environment variable.

The default configuration file is named ``repos.yml`` where `appdirs <https://pypi.python.org/pypi/appdirs>`_.user_config_dir is
(usually ~/.config/git-autoshare/).
This location can be configured with the ``GIT_AUTOSHARE_CONFIG_DIR`` environment variable.

By default ``git-autoshare`` invokes ``git`` as ``/usr/bin/git``. This can be configured with the ``GIT_AUTOSHARE_GIT_BIN``
environment variable.

An environment variable is used when launching tests (to avoid configuration retrieval issue) : ``GIT_AUTOSHARE_MODE``. Which takes only one value: 'test'.


Credits
~~~~~~~

Author:

  * Stéphane Bidoul (`ACSONE <https://acsone.eu/>`__)

Contributors

  * Simone Orsi (`Camptocamp <https://camptocamp.com/>`__)
  * Mykhailo Panarin
  * Stéphane Mangin

Maintainer:

.. image:: https://www.acsone.eu/logo.png
   :alt: ACSONE SA/NV
   :target: https://www.acsone.eu

This project is maintained by ACSONE SA/NV.
