git-autoshare
=============

.. image:: https://img.shields.io/badge/license-GPL--3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0-standalone.html
   :alt: License: GPL-3
.. image:: https://badge.fury.io/py/git-autoshare.svg
    :target: http://badge.fury.io/py/git-autoshare
.. image:: https://travis-ci.org/acsone/git-autoshare.svg?branch=master
   :target: https://travis-ci.org/acsone/git-autoshare
.. image:: https://coveralls.io/repos/acsone/git-autoshare/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/acsone/git-autoshare?branch=master

``git-autoshare`` is a git wrapper that automatically uses the ``--reference`` 
option of ``git clone`` to save disk space and download time.

Installation
~~~~~~~~~~~~

To install git-autoshare in a fancy way, we recommend using `pipsi <https://github.com/mitsuhiko/pipsi>`_.

Pipsi is a powerful tool which allows you to install Python scripts into isolated virtual environments.

To install pipsi, first run this::

    $ curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python

Follow the instructions, you'll have to update your ``PATH`` and make sure the script directory
comes before git in your ``PATH``.

Then simply run::

    $ pipsi install git-autoshare

To upgrade git-autoshare at any time::

    $ pipsi upgrade git-autoshare

git-autoshare installs itself both as a ``git`` executable, and a ``git-autoshare`` executable.

Usage
~~~~~

git clone
---------

By default, the git-autoshare provided ``git`` executable should be completely transparent and 
behave exactly as git.

To configure it, create a file named ``git-autoshare/repos.yml`` in your user configuration 
directory (often ``~/.config`` on Linux). This file must have the following structre::

    host:
        repo:
            - organization
            - ...
        ...:
    ...:

It lists all git hosts, repositories, and orgnizations that are subject to the sharing
of git objects. Here is an example::

    github.com:
        odoo:
            - odoo
            - OCA
        mis-buidler:
            - OCA
            - acsone

When configuring like this, when you git clone the odoo or mis-builder repositories, 
from one of these github organizations, git-autoshare will automatically insert the
--reference option in the git command.

For instance::

    $ git clone https://github.com/odoo/odoo

Will be transformed into::

    $ /usr/bin/git clone --reference ~/.cache/git-autoshare/github.com/odoo https://github.com/odoo/odoo


git prefetch
------------

git-autoshare adds a prefetch command that is mostly meant to be run in a cron job::

    $ git prefetch

will update the cache directory by fetching all repositories mentioned in repos.yml.

It can also prefetch one single repository, for example::

    $ git prefetch https://github.com/odoo/odoo.git

