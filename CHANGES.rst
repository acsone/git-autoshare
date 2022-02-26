Changes
~~~~~~~

1.0.0b6 (2022-02-26)
---------------------
- fix a regression where the GIT_AUTOSHARE_MODE environment variable became necessary

1.0.0b5 (2022-01-26)
---------------------
- support organization wildcards in git-autoshare-prefetch
- support python >= 3.6 only (no code change yet, only stop testing)

1.0.0b4 (2019-07-14)
--------------------
- support ssh:// urls, remove dependency on giturlparse

1.0.0b3 (2019-07-13)
--------------------
- always prefetch cache before cloning, to make sure the cache is updated
  regularly

1.0.0b2 (2019-03-17)
--------------------
- add submodule-add command
- use safe_load to parse configuration
- allow wildcards in configuration
- internal refactoring

1.0.0b1 (2018-01-07)
--------------------
- support for private repositories
- better handling of remotes in prefetch
- prefetch with --prun

1.0.0a2 (2017-10-10)
--------------------
- first packaged version
