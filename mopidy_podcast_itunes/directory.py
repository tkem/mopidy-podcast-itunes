from __future__ import unicode_literals

import logging
import requests
import urlparse

from mopidy_podcast.directory import PodcastDirectory
from mopidy_podcast.models import Ref

from . import Extension

_ATTRIBUTE_MAPPING = {
    None: None,
    'title': 'titleTerm',
    'author': 'authorTerm',
    'category': 'genreTerm',  # undocumented
    'description': 'descriptionTerm',
    'keywords': 'keywordsTerm'
}

_CHARTS_PATH = '/WebObjects/MZStoreServices.woa/ws/charts'
_GENRES_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'
_LOOKUP_PATH = '/lookup'
_SEARCH_PATH = '/search'

# absolute limit defined by iTunes API
_CHARTS_LIMIT = _SEARCH_LIMIT = 200

logger = logging.getLogger(__name__)


def _podcast_ref(item):
    uri, _ = urlparse.urldefrag(item.get('feedUrl'))
    return Ref.podcast(uri=uri, name=item.get('trackName'))


def _genre_ref(item, base):
    uri = urlparse.urljoin(base, item.get('id') + '/')
    return Ref.directory(uri=uri, name=item.get('name'))


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    _root_genre = None

    def __init__(self, config):
        super(iTunesDirectory, self).__init__(config)
        self.config = config[Extension.ext_name]
        self.timeout = self.config['timeout']
        self.display_name = self.config['display_name']

        base_url = self.config['base_url']
        self._charts_url = urlparse.urljoin(base_url, _CHARTS_PATH)
        self._genres_url = urlparse.urljoin(base_url, _GENRES_PATH)
        self._lookup_url = urlparse.urljoin(base_url, _LOOKUP_PATH)
        self._search_url = urlparse.urljoin(base_url, _SEARCH_PATH)
        self._session = requests.Session()

    def browse(self, uri, limit=None):
        genre, charts = self._genres(), None
        for p in uri.split('/'):
            if p.isdigit():
                genre = genre['subgenres'][p]
            else:
                charts = p
        if charts or 'subgenres' not in genre:
            return map(_podcast_ref, self._charts(genre, limit))
        subgenres = genre.get('subgenres', {})
        charts_uri = urlparse.urljoin(uri, 'charts')
        charts_label = self.config['charts_label'].format(
            genre.get('name'), genre.get('id')
        )
        refs = [Ref.directory(uri=charts_uri, name=charts_label)]
        refs.extend(_genre_ref(item, uri) for item in subgenres.values())
        return refs

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not terms or attr not in _ATTRIBUTE_MAPPING:
            return None
        if type == Ref.EPISODE:
            return None
        result = self._request(self._search_url, params={
            'term': ' '.join(terms),  # plus-escaped by requests
            'country': self.config['country'],
            'media': 'podcast',
            'entity': 'podcast',
            'attribute': _ATTRIBUTE_MAPPING[attr],
            'limit': min(limit, _SEARCH_LIMIT) if limit else None,
            'explicit': self.config['explicit']
        })
        return [_podcast_ref(item) for item in result.get('results', [])]

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
