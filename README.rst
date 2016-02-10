Mopidy-Podcast-iTunes
========================================================================

Mopidy-Podcast-iTunes is a Mopidy-Podcast_ extension for searching and
browsing podcasts on the `Apple iTunes Store
<https://itunes.apple.com/genre/podcasts/id26>`_.


Installation
------------------------------------------------------------------------

On Debian Linux and Debian-based distributions like Ubuntu or
Raspbian, please install the ``mopidy-podcast-itunes`` package from
apt.mopidy.com_::

  apt-get install mopidy-podcast-itunes

Otherwise, install the package from PyPI_::

  pip install Mopidy-Podcast-iTunes


Configuration
------------------------------------------------------------------------

The following configuration values are available:

- ``podcast-itunes/enabled``: Whether this extension should be enabled
  or not.  Defaults to ``true``.

- ``podcast-itunes/base_url``: The base URL for the iTunes Store.
  Defaults to ``http://itunes.apple.com/``.

- ``podcast-itunes/country``: The ISO country code for the iTunes
  Store you want to connect to.  Defaults to ``US``.

- ``podcast-itunes/root_genre_id``: The iTunes Store genre ID used as
  the root for browsing.  Defaults to ``26``, which is "Podcasts".

- ``podcast-itunes/timeout``: The HTTP request timeout in seconds when
  connecting to the iTunes Store.  Defaults to ``10``.


Project Resources
------------------------------------------------------------------------

.. image:: https://img.shields.io/pypi/v/Mopidy-Podcast-iTunes.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-Podcast-iTunes.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/tkem/mopidy-podcast-itunes/master.svg?style=flat
    :target: https://travis-ci.org/tkem/mopidy-podcast-itunes
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/tkem/mopidy-podcast-itunes/master.svg?style=flat
   :target: https://coveralls.io/r/tkem/mopidy-podcast-itunes?branch=master
   :alt: Test coverage

- `Issue Tracker`_
- `Source Code`_
- `Change Log`_


License
------------------------------------------------------------------------

Copyright (c) 2014-2016 Thomas Kemmer.

Licensed under the `Apache License, Version 2.0`_.


.. _Mopidy-Podcast: https://github.com/tkem/mopidy-podcast

.. _apt.mopidy.com: http://apt.mopidy.com/>
.. _PyPI: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/
.. _Issue Tracker: https://github.com/tkem/mopidy-podcast-itunes/issues/
.. _Source Code: https://github.com/tkem/mopidy-podcast-itunes/
.. _Change Log: https://github.com/tkem/mopidy-podcast-itunes/blob/master/CHANGES.rst

.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
