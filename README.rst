*************
Mopidy-Dirble
*************

.. image:: https://img.shields.io/pypi/v/Mopidy-Dirble.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Dirble/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-Dirble.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Dirble/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/mopidy/mopidy-dirble/master.svg?style=flat
    :target: https://travis-ci.org/mopidy/mopidy-dirble
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/mopidy/mopidy-dirble/master.svg?style=flat
   :target: https://coveralls.io/r/mopidy/mopidy-dirble?branch=master
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
    api_key = a4c8107f8fe57c235ce48df846720b9c816e8584
    countries = US,GB,NO
    timeout = 5000


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-dirble>`_
- `Issue tracker <https://github.com/mopidy/mopidy-dirble/issues>`_
- `Download development snapshot <https://github.com/mopidy/mopidy-dirble/tarball/master#egg=Mopidy-Dirble-dev>`_


Changelog
=========

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
