# References:
# noqa http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html
# noqa http://www.apple.com/itunes/affiliates/resources/documentation/genre-mapping.html

from __future__ import unicode_literals

import logging
import requests
import time

from urlparse import urljoin

from mopidy_podcast.directory import PodcastDirectory
from mopidy_podcast.models import Ref

PODCASTS_ID = '26'  # TODO: configure?
CHARTS_NAME = 'audioPodcasts'  # TODO: configure, name

LOOKUP_PATH = '/lookup'
SEARCH_PATH = '/search'
GENRES_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'
CHARTS_PATH = '/WebObjects/MZStoreServices.woa/ws/charts'
# noqa https://itunes.apple.com/WebObjects/MZStoreServices.woa/ws/charts?cc=de&g=1301&name=VideoPodcasts&limit=10

BROWSE_LIMIT = 20  # config

logger = logging.getLogger(__name__)


def _to_refs(results):
    refs = []
    for result in results:
        trackId = result.get('trackId')
        if 'feedUrl' not in result:
            logger.warn('Missing feedUrl for iTunes trackId %r', trackId)
            continue
        name = result.get('trackName', 'iTunes trackId %r' % trackId)
        refs.append(Ref.podcast(uri=result['feedUrl'], name=name))
    return refs


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    def __init__(self, backend):
        super(iTunesDirectory, self).__init__(backend)
        self.label = self.config['label']
        self.session = requests.Session()
        self.lookup_url = urljoin(self.config['base_url'], LOOKUP_PATH)
        self.search_url = urljoin(self.config['base_url'], SEARCH_PATH)
        self.genres_url = urljoin(self.config['base_url'], GENRES_PATH)
        self.charts_url = urljoin(self.config['base_url'], CHARTS_PATH)
        self.genre = self.get_genre(PODCASTS_ID)

    @property
    def config(self):
        return self.backend.config['podcast-itunes']

    def browse(self, path):
        genre = self.get_genre(PODCASTS_ID)
        for id in path.split('/'):
            if not id:
                continue  # absolute path
            elif id in genre.get('subgenres', {}):
                genre = genre['subgenres'][id]
            else:
                logger.warn('Invalid iTunes genre: %s', id)
        refs = _to_refs(self.get_charts(genre))
        for id, node in genre.get('subgenres', {}).items():
            uri = path + '/' + id
            ref = Ref.directory(uri=uri, name=node['name'])
            refs.append(ref)
        return refs

    def search(self, terms=None, attribute=None):
        if not terms:
            return []
        result = self.request(self.search_url, params={
            'term': '+'.join(terms),
            'country': self.config['country'],
            'media': 'podcast',
            'entity': 'podcast',
            'attribute': ATTRIBUTES[attribute] if attribute else None,
            'limit': self.config['limit'],
            'explicit': self.config['explicit']
        })
        return _to_refs(result.get('results', []))

    def get_genre(self, id):
        if getattr(self, 'genre', None) and self.genre['id'] == id:
            return self.genre
        result = self.request(self.genres_url, params={'id': id})
        genre = result.get(id)
        self.get_charts(genre)  # preload
        return genre

    def get_charts(self, genre):
        if not genre:
            return None
        if '_charts' in genre:
            charts = genre['_charts']
            expired = time.time() - 60  # config
            if charts['_updated'] > expired:
                return charts.get('results', [])
            else:
                logger.debug('iTunes charts cache expired: %s', genre)
        result = self.request(self.charts_url, params={
            'g': genre['id'],
            'cc': self.config['country'],
            'name': CHARTS_NAME,
            'limit': BROWSE_LIMIT
        })
        charts = self.request(self.lookup_url, params={
            'id': ','.join(str(id) for id in result.get('resultIds', []))
        })
        charts['_updated'] = time.time()
        genre['_charts'] = charts
        return charts.get('results', [])

    def request(self, url, params=None):
        timeout = self.config['timeout']
        response = self.session.get(url, params=params, timeout=timeout)
        return response.json()
