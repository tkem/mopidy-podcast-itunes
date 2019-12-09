*********************
Mopidy-Podcast-iTunes
*********************

.. image:: https://img.shields.io/pypi/v/Mopidy-Podcast-iTunes
    :target: https://pypi.org/project/Mopidy-Podcast-iTunes/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/circleci/build/gh/tkem/mopidy-podcast-itunes
    :target: https://circleci.com/gh/tkem/mopidy-podcast-itunes
    :alt: CircleCI build status

.. image:: https://img.shields.io/codecov/c/gh/tkem/mopidy-podcast-itunes
    :target: https://codecov.io/gh/tkem/mopidy-podcast-itunes
    :alt: Test coverage

Mopidy-Podcast-iTunes is a Mopidy_ extension for searching and
browsing podcasts on the `Apple iTunes Store
<https://itunes.apple.com/genre/podcasts/id26>`_.

.. _Mopidy: http://www.mopidy.com/


Installation
============

On Debian Linux and Debian-based distributions like Ubuntu or
Raspbian, install the ``mopidy-podcast-itunes`` package from
apt.mopidy.com_::

  apt-get install mopidy-podcast-itunes

Otherwise, install the Python package from PyPI_::

  pip install Mopidy-Podcast-iTunes

.. _apt.mopidy.com: http://apt.mopidy.com/
.. _PyPI: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/


Configuration
=============

The following configuration values are available:

- ``podcast-itunes/enabled``: Whether this extension should be enabled
  or not.  Defaults to ``true``.

- ``podcast-itunes/base_url``: The base URL for the iTunes Store.
  Defaults to ``http://itunes.apple.com/``.

- ``podcast-itunes/country``: The ISO country code for the store to be
  used.  Defaults to ``US``.

- ``podcast-itunes/explicit``: Whether search results should include
  explicit content.  Can be set to ``Yes``, ``No``, or left empty to
  use the store's default.

- ``podcast-itunes/charts``: One of ``podcasts``, ``audioPodcasts`` or
  ``videoPodcasts``.  Defaults to ``audioPodcasts``.

- ``podcast-itunes/charts_limit``: The maximum number of charts
  entries to retrieve.  Defaults to ``20``.

- ``podcast-itunes/search_limit``: The maximum number of search
  results to retrieve.  Defaults to ``20``.

- ``podcast-itunes/timeout``: The HTTP request timeout in seconds when
  connecting to the iTunes Store.  Defaults to ``10``.

- ``podcast-itunes/retries``: The maximum number of HTTP connection
  retries when connecting to the iTunes Store.  Defaults to ``3``.


Project Resources
=================

- `Source code <https://github.com/tkem/mopidy-podcast-itunes>`_
- `Issue tracker <https://github.com/tkem/mopidy-podcast-itunes/issues>`_
- `Changelog <https://github.com/tkem/mopidy-podcast-itunes/blob/master/CHANGELOG.rst>`_


Credits
=======

- Original author: `Thomas Kemmer <https://github.com/tkem>`__
- Current maintainer: `Thomas Kemmer <https://github.com/tkem>`__
- `Contributors <https://github.com/tkem/mopidy-podcast-itunes/graphs/contributors>`_
