Mopidy-Podcast-iTunes
========================================================================

Mopidy-Podcast-iTunes is a Mopidy-Podcast_ extension for searching and
browsing podcasts on the `Apple iTunes Store`_.


Installation
------------------------------------------------------------------------

First, make sure you have Mopidy-Podcast version 1.0.0 or later
installed.  Then Mopidy-Podcast-iTunes can be installed by running::

    pip install Mopidy-Podcast-iTunes

After a restart, Mopidy-Podcast will pick up the installed extension
automatically.

You can also install Debian/Ubuntu packages from the `APT repository`_::

    wget -q -O - http://apt.kemmer.co.at/tkem.gpg | sudo apt-key add -
    sudo wget -q -O /etc/apt/sources.list.d/tkem.list http://apt.kemmer.co.at/tkem.list
    sudo apt-get update
    sudo apt-get install mopidy-podcast-itunes


Configuration
------------------------------------------------------------------------

The default configuration contains everything to get you up and
running, and will usually require only a few modifications to match
personal preferences::

    [podcast-itunes]
    enabled = true

    # iTunes Store base URL
    base_url = http://itunes.apple.com/

    # user-friendly name for browsing the iTunes Store
    root_name = iTunes Store

    # format string for genre results; field names: id, name, url
    genre_format = {name}

    # format string for podcast results; field names: collectionId,
    # collectionName, country, kind, trackCount
    podcast_format = {collectionName}

    # format string for episode results; field names: collectionId,
    # collectionName, country, episodeContentType, episodeFileExtension,
    # episodeGuid, kind, releaseDate, trackId, trackName
    episode_format = {trackName} [{collectionName}]

    # charts to display when browsing; possible values: "Podcasts",
    # "AudioPodcasts", "VideoPodcasts"
    charts = AudioPodcasts

    # directory name to display for browsing charts of a genre/category
    # with subgenres; field names as for 'genre_format'
    charts_format = All {name}

    # ISO country code for the iTunes Store you want to use
    country = US

    # whether you want to include explicit content in your search
    # results; possible values: "Yes", "No", or store default (blank)
    explicit =

    # HTTP request timeout in seconds
    timeout = 10


Project Resources
------------------------------------------------------------------------

.. image:: http://img.shields.io/pypi/v/Mopidy-Podcast-iTunes.svg
    :target: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/
    :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/Mopidy-Podcast-iTunes.svg
    :target: https://pypi.python.org/pypi/Mopidy-Podcast-iTunes/
    :alt: Number of PyPI downloads

- `Issue Tracker`_
- `Source Code`_
- `Change Log`_
- `Development Snapshot`_


License
------------------------------------------------------------------------

Copyright (c) 2014 Thomas Kemmer.

Licensed under the `Apache License, Version 2.0`_.


.. _Mopidy-Podcast: https://github.com/tkem/mopidy-podcast
.. _Apple iTunes Store: https://itunes.apple.com/genre/podcasts/id26
.. _APT repository: http://apt.kemmer.co.at/
.. _Issue Tracker: https://github.com/tkem/mopidy-podcast-itunes/issues/
.. _Source Code: https://github.com/tkem/mopidy-podcast-itunes
.. _Change Log: https://raw.github.com/tkem/mopidy-podcast-itunes/master/Changes
.. _Development Snapshot: https://github.com/tkem/mopidy-podcast-itunes/tarball/master#egg=Mopidy-Podcast-iTunes-dev

.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
