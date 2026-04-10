:tocdepth: 3

*********************
Mopidy-Podcast-iTunes
*********************

Mopidy-Podcast-iTunes is a Mopidy_ extension for searching and
browsing podcasts on `Apple Podcasts`_, using the `iTunes Search
API`_.


*************
Configuration
*************

This extension provides a number of configuration values that can be
tweaked.  However, the :ref:`default configuration <defconf>` should
contain everything to get you up and running, and will usually require
only a few modifications, if any, to match personal preferences.


.. _confvals:

Configuration Values
====================

.. confval:: podcast-itunes/enabled

   Whether this extension should be enabled or not.

.. confval:: podcast-itunes/base_url

   The iTunes Search API base URL.

.. confval:: podcast-itunes/country

   The two-letter country code for the store you want to search.

.. confval:: podcast-itunes/explicit

   Whether you want to include explicit content in your search results.

.. confval:: podcast-itunes/charts_limit

   The maximum number of podcast charts entries to retrieve when browsing.

.. confval:: podcast-itunes/search_limit

   The maximum number of search results to retrieve.

.. confval:: podcast-itunes/timeout

   The HTTP request timeout in seconds when using the Search API.

.. confval:: podcast-itunes/retries

   The maximum number of HTTP connection retries when using the Search API.


.. _defconf:

Default Configuration
=====================

For reference, this is the default configuration shipped with
Mopidy-Podcast-iTunes release |release|:

.. literalinclude:: ../src/mopidy_podcast_itunes/ext.conf
   :language: ini

.. _Mopidy: https://www.mopidy.com/
.. _Apple Podcasts: https://podcasts.apple.com/
.. _iTunes Search API: https://performance-partners.apple.com/search-api
