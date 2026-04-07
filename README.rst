*********************
Mopidy-Podcast-iTunes
*********************

.. image:: https://img.shields.io/pypi/v/Mopidy-Podcast-iTunes
    :target: https://pypi.org/project/Mopidy-Podcast-iTunes/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/github/actions/workflow/status/tkem/mopidy-podcast-itunes/ci.yml
   :target: https://github.com/tkem/mopidy-podcast-itunes/actions/workflows/ci.yml
   :alt: CI build status

.. image:: https://img.shields.io/codecov/c/gh/tkem/mopidy-podcast-itunes
    :target: https://codecov.io/gh/tkem/mopidy-podcast-itunes
    :alt: Test coverage

.. image:: https://img.shields.io/github/license/tkem/mopidy-podcast-itunes
   :target: https://raw.github.com/tkem/mopidy-podcast-itunes/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

Mopidy-Podcast-iTunes is a Mopidy_ extension for searching and
browsing podcasts on `Apple Podcasts`_, using the `iTunes Search
API`_.

.. _Apple Podcasts: https://podcasts.apple.com/
.. _iTunes Search API: https://performance-partners.apple.com/search-api
.. _Mopidy: https://www.mopidy.com/


Installation
============

On Debian Linux and Debian-based distributions like Ubuntu or
Raspbian, install the ``mopidy-podcast-itunes`` package from
apt.mopidy.com_::

  apt-get install mopidy-podcast-itunes

Otherwise, install the Python package from PyPI_::

  pip install Mopidy-Podcast-iTunes

.. _apt.mopidy.com: https://apt.mopidy.com/
.. _PyPI: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/


Configuration
=============

The following configuration values are available:

- ``podcast-itunes/enabled``: Whether this extension should be enabled
  or not.  Defaults to ``true``.

- ``podcast-itunes/base_url``: The iTunes Search API base URL.
  Defaults to ``https://itunes.apple.com/``.

- ``podcast-itunes/country``: The two-letter country code for the
  store you want to search.  Defaults to ``US``.

- ``podcast-itunes/explicit``: A flag indicating whether or not you
  want to include explicit content in your search results.  Can be set
  to ``Yes`` or ``No``.   The default is ``Yes``.

- ``podcast-itunes/charts_limit``: The maximum number of podcast
  charts entries to retrieve when browsing.  Defaults to ``20``.

- ``podcast-itunes/search_limit``: The maximum number of search
  results to retrieve.  Defaults to ``20``.

- ``podcast-itunes/timeout``: The HTTP request timeout in seconds when
  using the Search API.  Defaults to ``10``.

- ``podcast-itunes/retries``: The maximum number of HTTP connection
  retries when using the Search API.  Defaults to ``3``.


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
