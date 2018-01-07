git-autoshare
=============

.. image:: https://img.shields.io/badge/license-GPL--3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0-standalone.html
   :alt: License: GPL-3
.. image:: https://badge.fury.io/py/git-autoshare.svg
    :target: http://badge.fury.io/py/git-autoshare
.. image:: https://travis-ci.org/acsone/git-autoshare.svg?branch=master
   :target: https://travis-ci.org/acsone/git-autoshare
.. image:: https://codecov.io/gh/acsone/git-autoshare/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/acsone/git-autoshare

A git clone wrapper that automatically uses `--reference 
<https://git-scm.com/docs/git-clone#git-clone---reference-if-ableltrepositorygt>`_
to save disk space and download time.

.. contents::

Installation
~~~~~~~~~~~~

To install git-autoshare in a fancy way, we recommend using `pipsi <https://github.com/mitsuhiko/pipsi>`_.

Pipsi is a powerful tool which allows you to install Python scripts into isolated virtual environments.

To install pipsi, first run this::

    $ curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python

Follow the instructions, you'll have to update your ``PATH``.

Then simply run::

    $ pipsi install git-autoshare

To upgrade git-autoshare at any time::

    $ pipsi upgrade git-autoshare

If you want ``git autoshare-clone`` to be invoked transparently in place of ``git clone``, 
create the following bash script, name it ``git``, and place it in your ``PATH`` before ``/usr/bin/git``:

  .. code:: bash

    #!/bin/bash
    if [ "$1" == "clone" ]
    then
        shift
        /usr/bin/git autoshare-clone "$@"
    else
        /usr/bin/git "$@"
    fi

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

git autoshare-clone command
---------------------------

If configured like the example above, when you git clone the odoo or mis-builder repositories 
from one of these github organizations, ``git autoshare-clone`` will automatically insert the
``--reference`` option in the git clone command. For example::

    $ git autoshare-clone https://github.com/odoo/odoo

will be transformed into::

    $ /usr/bin/git clone --reference ~/.cache/git-autoshare/github.com/odoo https://github.com/odoo/odoo


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

Credits
~~~~~~~

Author:

  * Stéphane Bidoul (`ACSONE <http://acsone.eu/>`_)

Maintainer:

.. image:: https://www.acsone.eu/logo.png
   :alt: ACSONE SA/NV
   :target: https://www.acsone.eu

This project is maintained by ACSONE SA/NV.
