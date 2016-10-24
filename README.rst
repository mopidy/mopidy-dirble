*************
Mopidy-Dirble
*************

.. image:: https://img.shields.io/pypi/v/Mopidy-Dirble.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Dirble/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/mopidy/mopidy-dirble/develop.svg?style=flat
    :target: https://travis-ci.org/mopidy/mopidy-dirble
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/mopidy/mopidy-dirble/develop.svg?style=flat
   :target: https://coveralls.io/r/mopidy/mopidy-dirble?branch=develop
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for Dirble open radio directory.


Installation
============

Debian/Ubuntu/Raspbian: Install the ``mopidy-dirble`` package from
`apt.mopidy.com <http://apt.mopidy.com/>`_::

    sudo apt-get install mopidy-dirble

Arch Linux: Install the ``mopidy-dirble`` package from
`AUR <https://aur.archlinux.org/packages/mopidy-dirble/>`_::

    sudo yaourt -S mopidy-dirble

OS X: Install the ``mopidy-dirble`` package from the
`mopidy/mopidy <https://github.com/mopidy/homebrew-mopidy>`_ Homebrew tap::

    brew install mopidy-dirble

Else: Install the the package from PyPI::

    pip install Mopidy-Dirble


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-Dirble to your Mopidy configuration file::

    [dirble]
    api_key = INSERT-YOUR-API-KEY-FROM-DIRBLE-HERE
    countries = US,GB,NO
    timeout = 5000

To get this working you must first go to `Dirble <https://dirble.com>`_ and
sign up for an account or just login with Facebook or Twitter. Then go to the
`API keys page <https://dirble.com/users/apikeys>`_ and get your API key.
The free plan should be more than enough for a typical Mopidy install.


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-dirble>`_
- `Issue tracker <https://github.com/mopidy/mopidy-dirble/issues>`_


Credits
=======

- Original author: `Thomas Adamcik <https://github.com/adamcik>`__
- Current maintainer: `Thomas Adamcik <https://github.com/adamcik>`__
- `Contributors <https://github.com/mopidy/mopidy-dirble/graphs/contributors>`_


Changelog
=========

v1.3.0 (2016-01-25)
-------------------

- Fix user country handling. Fixes #12
- Log an error for bad API tokens.
- Various internal cleanups
- Removed bad sample API key and added instructions to get your own. Fixes #13

v1.2.0 (2015-12-05)
-------------------

- Update to account for changes in data from Dirble API. Fixes #11

- pycountry is no longer used as Dirble provides names now.

v1.1.2 (2015-06-25)
-------------------

- Fix image handling bugs in 1.1.1.

v1.1.1 (2015-06-24)
-------------------

- Updates to match Dirble v2 API changes.

- Prefer streams that Dirble says are up. Thanks to Alexander Hartl
  (@alexhartl) for suggesting the status check in PR#8.

v1.1.0 (2015-04-26)
-------------------

- Use Requests for accessing the API.

- Update to use new Dirble v2 APIs.

- Add support for station images.

- Add continent/country browsing.

- Add search support.

- Stop showing country codes in country folders.

v1.0.0 (2015-03-25)
-------------------

- Require Mopidy >= 1.0.

- Update to work with new playback API in Mopidy 1.0.

- Update to work with new backend search API in Mopidy 1.0.

v0.1.1 (2014-03-20)
-------------------

- Change to new API endpoint URL. The old API endpoint will be discontinued
  2014-05-03.

v0.1.0 (2014-01-20)
-------------------

- Initial release.

- Provides basic hierarchy based browsing of Dirble categories and
  sub-categories.

- Lists user defined countries.
