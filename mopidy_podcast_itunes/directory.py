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


def _to_podcast_ref(item):
    uri, _ = urlparse.urldefrag(item.get('feedUrl'))
    return Ref.podcast(uri=uri, name=item.get('trackName'))


def _to_genre_ref(item):
    uri = item.get('id') + '/'
    return Ref.directory(uri=uri, name=item.get('name'))


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    _root_genre = {}

    _root_genre_id = '26'  # Podcasts

    def __init__(self, config):
        super(iTunesDirectory, self).__init__(config)
        self.root_name = config[Extension.ext_name]['name']
        self._charts = config[Extension.ext_name]['charts']
        self._charts_label = config[Extension.ext_name]['charts_label']
        self._country = config[Extension.ext_name]['country']
        self._explicit = config[Extension.ext_name]['explicit']
        self._timeout = config[Extension.ext_name]['timeout']

        base_url = config[Extension.ext_name]['base_url']
        self._charts_url = urlparse.urljoin(base_url, _CHARTS_PATH)
        self._genres_url = urlparse.urljoin(base_url, _GENRES_PATH)
        self._lookup_url = urlparse.urljoin(base_url, _LOOKUP_PATH)
        self._search_url = urlparse.urljoin(base_url, _SEARCH_PATH)
        self._session = requests.Session()

    def browse(self, uri, limit=None):
        genre = self._root_genre
        subgenres = {}
        charts = None
        for p in uri.split('/'):
            subgenres = genre.get('subgenres', {})
            if p in subgenres:
                genre = subgenres[p]
            else:
                charts = p
        if charts or not subgenres:
            return map(_to_podcast_ref, self._get_charts(genre, charts, limit))
        charts_name = self._charts_label.format(genre.get('name'))
        refs = [Ref.directory(uri=self._charts, name=charts_name)]
        refs.extend(map(_to_genre_ref, subgenres.values()))
        return refs

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not terms or attr not in _ATTRIBUTE_MAPPING:
            return None
        if type == Ref.EPISODE:
            return None
        result = self._request(self._search_url, params={
            'term': ' '.join(terms),  # plus-escaped by requests
            'country': self._country,
            'media': 'podcast',
            'entity': 'podcast',
            'attribute': _ATTRIBUTE_MAPPING[attr],
            'limit': min(limit, _SEARCH_LIMIT) if limit else None,
            'explicit': self._explicit
        })
        return map(_to_podcast_ref, result.get('results', []))

    def refresh(self, uri=None):
        result = self._request(self._genres_url, params={
            'id': self._root_genre_id,
            'cc': self._country
        })
        self._root_genre = result.get(self._root_genre_id)

    def _get_charts(self, genre, charts=None, limit=None):
        if '_charts' not in genre or genre['_charts']['_limit'] < limit:
            result = self._request(self._charts_url, params={
                'g': genre['id'],
                'cc': self._country,
                'name': charts or self._charts,
                'limit': min(limit, _CHARTS_LIMIT) if limit else None
            })
            charts = self._request(self._lookup_url, params={
                'id': ','.join(str(id) for id in result.get('resultIds', []))
            })
            charts['_limit'] = limit
            genre['_charts'] = charts
        return genre['_charts'].get('results', [])[:limit]

    def _request(self, url, params=None):
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        logger.debug('Retrieving %s took %s', response.url, response.elapsed)
        return response.json()
