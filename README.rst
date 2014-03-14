Mopidy-Podcast-iTunes
========================================================================

Mopidy-Podcast-iTunes is a Mopidy-Podcast_ extension for searching and
browsing podcasts on the `iTunes Store`_.


Installation
------------------------------------------------------------------------

Like other Mopidy extensions, Mopidy-Podcast-iTunes can be installed
using pip by running::

    pip install Mopidy-Podcast-iTunes

You can also download and install Debian/Ubuntu packages for
Mopidy-Podcast-iTunes releases_.


Configuration
------------------------------------------------------------------------

Configuration items are still subject to change at this point, so be
warned::

    [podcast-itunes]
    enabled = true

    # user-friendly name for browsing, etc.
    display_name = iTunes Store

    # iTunes Store base URL
    base_url = http://itunes.apple.com/

    # ISO country code for the store you want to search
    country = US

    # iTunes charts to return when browsing
    browse_charts = AudioPodcasts

    # number of charts results you want the iTunes Store to return
    browse_limit = 20

    # iTunes genre ID for browsing (26: Podcasts)
    root_genre_id = 26

    # whether you want to include explicit content in your search
    # results; possible values: "Yes", "No", or default (blank)
    explicit =

    # optional http request timeout in seconds
    timeout =


Project Resources
------------------------------------------------------------------------

- `Source Code`_
- `Issue Tracker`_
- `Change Log`_
- `Development Snapshot`_

.. image:: https://pypip.in/v/Mopidy-Podcast-iTunes/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-Podcast-iTunes/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/
    :alt: Number of PyPI downloads


License
------------------------------------------------------------------------

Mopidy-Podcast-iTunes is Copyright 2014 Thomas Kemmer.

Licensed under the `Apache License, Version 2.0`_.


.. _Mopidy-Podcast: https://github.com/tkem/mopidy-podcast
.. _iTunes Store: https://itunes.apple.com/genre/podcasts/id26
.. _releases: https://github.com/tkem/mopidy-podcast-itunes/releases
.. _Source Code: https://github.com/tkem/mopidy-podcast-itunes
.. _Issue Tracker: https://github.com/tkem/mopidy-podcast-itunes/issues/
.. _Change Log: https://github.com/tkem/mopidy-podcast-itunes/blob/master/Changes
.. _Development Snapshot: https://github.com/tkem/mopidy-podcast-itunes/tarball/master#egg=Mopidy-Podcast-iTunes-dev
.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
