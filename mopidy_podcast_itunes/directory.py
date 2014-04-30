from __future__ import unicode_literals

import logging
import requests
import urlparse

from mopidy_podcast.directory import PodcastDirectory
from mopidy_podcast.models import Ref

from . import Extension

_ATTRIBUTES = {
    None: None,
    PodcastDirectory.TITLE: 'titleTerm',
    PodcastDirectory.AUTHOR: 'authorTerm',
    PodcastDirectory.CATEGORY: 'genreTerm',  # undocumented
    PodcastDirectory.DESCRIPTION: 'descriptionTerm',
    PodcastDirectory.KEYWORDS: 'keywordsTerm'
}

_CHARTS_PATH = '/WebObjects/MZStoreServices.woa/ws/charts'
_GENRES_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'
_LOOKUP_PATH = '/lookup'
_SEARCH_PATH = '/search'

# absolute limit defined by iTunes API
_CHARTS_LIMIT = _SEARCH_LIMIT = 200

logger = logging.getLogger(__name__)


def _wrap_podcast(item):
    uri, _ = urlparse.urldefrag(item.get('feedUrl'))
    return Ref.podcast(uri=uri, name=item.get('trackName'))


def _wrap_genre(item, base):
    uri = urlparse.urljoin(base + '/', item.get('id'))
    return Ref.directory(uri=uri, name=item.get('name'))


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    _root_genre = None

    def __init__(self, config, timeout):
        super(iTunesDirectory, self).__init__(config, timeout)
        self.config = config[Extension.ext_name]
        self.timeout = timeout
        self.display_name = self.config['display_name']

        base_url = self.config['base_url']
        self._charts_url = urlparse.urljoin(base_url, _CHARTS_PATH)
        self._genres_url = urlparse.urljoin(base_url, _GENRES_PATH)
        self._lookup_url = urlparse.urljoin(base_url, _LOOKUP_PATH)
        self._search_url = urlparse.urljoin(base_url, _SEARCH_PATH)
        self._session = requests.Session()

    def browse(self, uri, limit=None):
        _, _, path, query, _ = urlparse.urlsplit(uri)
        genre = self._genres()
        for genre_id in [p for p in path.split('/') if p]:
            genre = genre['subgenres'][genre_id]
        subgenres = genre.get('subgenres', {})
        if query == 'charts' or not subgenres:
            return [_wrap_podcast(item) for item in self._charts(genre, limit)]
        charts_uri = urlparse.urljoin(uri, '?charts')
        charts_label = self.config['charts_label'].format(
            genre.get('name'), genre.get('id')
        )
        refs = [Ref.directory(uri=charts_uri, name=charts_label)]
        refs.extend(_wrap_genre(item, uri) for item in subgenres.values())
        return refs

    def search(self, terms, attr=None, type=None, uri=None, limit=None):
        if not terms or attr not in _ATTRIBUTES:
            return None
        if type == Ref.EPISODE:
            return None
        result = self._request(self._search_url, params={
            'term': ' '.join(terms),  # plus-escaped by requests
            'country': self.config['country'],
            'media': 'podcast',
            'entity': 'podcast',
            'attribute': _ATTRIBUTES[attr],
            'limit': min(limit, _SEARCH_LIMIT) if limit else None,
            'explicit': self.config['explicit']
        })
        return [_wrap_podcast(item) for item in result.get('results', [])]

    def update(self):
        result = self._request(self._genres_url, params={
            'id': self.config['root_genre_id'],
            'cc': self.config['country']
        })
        self._root_genre = result.get(self.config['root_genre_id'])

    def _genres(self):
        if not self._root_genre:
            self.refresh()
        return self._root_genre

    def _charts(self, genre, limit=None):
        if '_charts' not in genre or genre['_charts']['_limit'] < limit:
            result = self._request(self._charts_url, params={
                'g': genre['id'],
                'cc': self.config['country'],
                'name': self.config['charts'],
                'limit': min(limit, _CHARTS_LIMIT) if limit else None
            })
            charts = self._request(self._lookup_url, params={
                'id': ','.join(str(id) for id in result.get('resultIds', []))
            })
            charts['_limit'] = limit
            genre['_charts'] = charts
        return genre['_charts'].get('results', [])[:limit]

    def _request(self, url, params=None):
        response = self._session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        logger.debug('Retrieving %s took %s', response.url, response.elapsed)
        return response.json()
