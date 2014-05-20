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

_ENTITY_MAPPING = {
    None: 'podcast,podcastEpisode',
    Ref.PODCAST: 'podcast',
    Ref.EPISODE: 'podcastEpisode'
}

_CHARTS_PATH = '/WebObjects/MZStoreServices.woa/ws/charts'
_GENRES_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'
_LOOKUP_PATH = '/lookup'
_SEARCH_PATH = '/search'

# absolute limit defined by iTunes API
_CHARTS_LIMIT = _SEARCH_LIMIT = 200

logger = logging.getLogger(__name__)


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    _root_genre = {}

    _root_genre_id = '26'  # Podcasts

    def __init__(self, config):
        super(iTunesDirectory, self).__init__(config)
        config = config[Extension.ext_name]

        self.root_name = config['name']
        self._charts = config['charts']
        self._country = config['country']
        self._explicit = config['explicit']
        self._timeout = config['timeout']

        self._genre_name = config['genre_name']
        self._charts_name = config['charts_name']
        self._podcast_name = config['podcast_name']
        self._episode_name = config['episode_name']

        base_url = config['base_url']
        self._charts_url = urlparse.urljoin(base_url, _CHARTS_PATH)
        self._genres_url = urlparse.urljoin(base_url, _GENRES_PATH)
        self._lookup_url = urlparse.urljoin(base_url, _LOOKUP_PATH)
        self._search_url = urlparse.urljoin(base_url, _SEARCH_PATH)
        self._session = requests.Session()

    def browse(self, uri, limit=None):
        genre, subgenres, charts = self._root_genre, {}, None
        for p in uri.split('/'):
            subgenres = genre.get('subgenres', {})
            if p in subgenres:
                genre = subgenres[p]
            else:
                charts = p
        if charts or not subgenres:
            return map(self._ref, self._get_charts(genre, charts, limit))
        charts_name = self._charts_name.format(**genre)
        refs = [Ref.directory(uri=self._charts, name=charts_name)]
        refs.extend(map(self._ref, subgenres.values()))
        return refs

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not terms or attr not in _ATTRIBUTE_MAPPING:
            return None
        g = uri.rsplit('/', 2)[1] if uri else None
        result = self._request(self._search_url, params={
            'term': ' '.join(terms),  # plus-escaped by requests
            'country': self._country,
            'media': 'podcast',
            'entity': _ENTITY_MAPPING[type],
            'attribute': _ATTRIBUTE_MAPPING[attr],
            'limit': min(limit, _SEARCH_LIMIT) if limit else _SEARCH_LIMIT,
            'explicit': self._explicit,
            'g': g or None  # undocumented
        })
        return map(self._ref, result.get('results', []))

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

    def _ref(self, item):
        if 'episodeUrl' in item:
            uri = urlparse.urljoin(item['feedUrl'], '#' + item['episodeUrl'])
            name = self._episode_name.format(**item)
            return Ref.episode(uri=uri, name=name)
        elif 'feedUrl' in item:
            uri, _ = urlparse.urldefrag(item['feedUrl'])
            name = self._podcast_name.format(**item)
            return Ref.podcast(uri=uri, name=name)
        else:
            uri = item['id'] + '/'
            name = self._genre_name.format(**item)
            return Ref.directory(uri=uri, name=name)
