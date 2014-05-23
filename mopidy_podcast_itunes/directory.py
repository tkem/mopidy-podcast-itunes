from __future__ import unicode_literals

import logging
import re
import requests
import string
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

_URI_GENRE_RE = re.compile(r"(\d*)/[^/]*$")

_CHARTS_PATH = '/WebObjects/MZStoreServices.woa/ws/charts'
_GENRES_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'
_LOOKUP_PATH = '/lookup'
_SEARCH_PATH = '/search'

# absolute limit defined by iTunes API
_CHARTS_LIMIT = _SEARCH_LIMIT = 200

logger = logging.getLogger(__name__)


class Formatter(string.Formatter):

    def get_value(self, key, args, kwargs):
        try:
            return super(Formatter, self).get_value(key, args, kwargs)
        except KeyError:
            return None


formatter = Formatter()


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    _root_genre = {}

    _root_genre_id = '26'  # Podcasts

    def __init__(self, config):
        super(iTunesDirectory, self).__init__(config)
        self._config = config[Extension.ext_name]
        self._session = requests.Session()

        base_url = self._config['base_url']
        self._charts_url = urlparse.urljoin(base_url, _CHARTS_PATH)
        self._genres_url = urlparse.urljoin(base_url, _GENRES_PATH)
        self._lookup_url = urlparse.urljoin(base_url, _LOOKUP_PATH)
        self._search_url = urlparse.urljoin(base_url, _SEARCH_PATH)

        self.root_name = self._config['root_name']  # for browsing

    def browse(self, uri, limit=None):
        genre, subgenres, charts = self._root_genre, {}, None
        for p in uri.split('/'):
            subgenres = genre.get('subgenres', {})
            if p in subgenres:
                genre = subgenres[p]
            else:
                charts = p
        if charts or not subgenres:
            return map(self._ref, self._charts(genre, charts, limit))
        # put charts entry first
        charts_uri = self._config['charts']
        charts_format = self._config['charts_format']
        charts_name = formatter.vformat(charts_format, [], genre)
        refs = [Ref.directory(uri=charts_uri, name=charts_name)]
        # append subgenre entries
        genre_format = self._config['genre_format']
        for subgenre in subgenres.values():
            uri = subgenre['id'] + '/'
            name = formatter.vformat(genre_format, [], subgenre)
            refs.append(Ref.directory(uri=uri, name=name))
        return refs

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not terms or attr not in _ATTRIBUTE_MAPPING:
            return None
        gmatch = _URI_GENRE_RE.search(uri or '/')
        result = self._request(self._search_url, params={
            'term': ' '.join(terms),  # plus-escaped by requests
            'media': 'podcast',
            'entity': _ENTITY_MAPPING[type],
            'attribute': _ATTRIBUTE_MAPPING[attr],
            'limit': min(limit, _SEARCH_LIMIT) if limit else _SEARCH_LIMIT,
            'country': self._config['country'],
            'explicit': self._config['explicit'],
            'g': gmatch.group(1) or None  # undocumented
        })
        return map(self._ref, result.get('results', []))

    def refresh(self, uri=None):
        try:
            result = self._request(self._genres_url, params={
                'id': self._root_genre_id,
                'cc': self._config['country']
            })
            self._root_genre = result.get(self._root_genre_id)
        except Exception as e:
            logger.error('Refreshing %s failed: %s', Extension.dist_name, e)

    def _charts(self, genre, charts=None, limit=None):
        if '_charts' not in genre or genre['_charts']['_limit'] < limit:
            result = self._request(self._charts_url, params={
                'g': genre['id'],
                'cc': self._config['country'],
                'name': charts or self._config['charts'],
                'limit': min(limit, _CHARTS_LIMIT) if limit else None
            })
            charts = self._request(self._lookup_url, params={
                'id': ','.join(map(str, result.get('resultIds', [])))
            })
            charts['_limit'] = limit
            genre['_charts'] = charts
        return genre['_charts'].get('results', [])[:limit]

    def _request(self, url, params=None):
        response = self._session.get(
            url,
            params=params,
            timeout=self._config['timeout']
        )
        response.raise_for_status()
        logger.debug('Retrieving %s took %s', response.url, response.elapsed)
        return response.json()

    def _ref(self, item):
        if 'episodeUrl' in item:
            uri = urlparse.urljoin(item['feedUrl'], '#' + item['episodeUrl'])
            name = formatter.vformat(self._config['episode_format'], [], item)
            return Ref.episode(uri=uri, name=name)
        else:
            uri, _ = urlparse.urldefrag(item['feedUrl'])
            name = formatter.vformat(self._config['podcast_format'], [], item)
            return Ref.podcast(uri=uri, name=name)
