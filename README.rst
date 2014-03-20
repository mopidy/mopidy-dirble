****************************
Mopidy-Dirble
****************************

.. image:: https://pypip.in/v/Mopidy-Dirble/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Dirble/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-Dirble/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Dirble/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/mopidy/mopidy-dirble.png?branch=master
    :target: https://travis-ci.org/mopidy/mopidy-dirble
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/mopidy/mopidy-dirble/badge.png?branch=master
   :target: https://coveralls.io/r/mopidy/mopidy-dirble?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for Dirble open radio directory.


Installation
============

Install by running::

    pip install Mopidy-Dirble

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


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
