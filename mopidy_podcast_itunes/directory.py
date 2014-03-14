from __future__ import unicode_literals

import logging
import requests

from urlparse import urljoin

from mopidy_podcast import PodcastDirectory
from mopidy_podcast.models import Ref

ATTRIBUTES = {
    None: None,
    PodcastDirectory.AUTHOR: 'authorTerm',
    PodcastDirectory.CATEGORY: None,  # TODO
    PodcastDirectory.DESCRIPTION: 'descriptionTerm',
    PodcastDirectory.KEYWORDS: 'keywordsTerm',
    PodcastDirectory.TITLE: 'titleTerm',
}

CHARTS_PATH = '/WebObjects/MZStoreServices.woa/ws/charts'
GENRES_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'
LOOKUP_PATH = '/lookup'
SEARCH_PATH = '/search'

logger = logging.getLogger(__name__)


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    genres = None

    def __init__(self, backend):
        super(iTunesDirectory, self).__init__(backend)
        self.display_name = self.config['display_name']
        self.charts_url = urljoin(self.config['base_url'], CHARTS_PATH)
        self.genres_url = urljoin(self.config['base_url'], GENRES_PATH)
        self.lookup_url = urljoin(self.config['base_url'], LOOKUP_PATH)
        self.search_url = urljoin(self.config['base_url'], SEARCH_PATH)
        self.session = requests.Session()
        self.refresh()

    @property
    def config(self):
        return self.backend.config['podcast-itunes']

    def browse(self, uri):
        if not self.genres:
            self.genres = self._genres(self.config['root_genre_id'])
        genre = self.genres
        for id in uri.split('/'):
            subgenres = genre.get('subgenres', {})
            if id in subgenres:
                genre = subgenres[id]
            elif not id:
                continue
            else:
                logger.warn('Invalid iTunes genre ID: %s', id)
        refs = [self._ref(item) for item in self._charts(genre)]
        for id, node in genre.get('subgenres', {}).items():
            name = node.get('name')
            ref = Ref.directory(uri=urljoin(uri, id + '/'), name=name)
            refs.append(ref)
        return refs

    def search(self, terms=None, attribute=None, limit=None):
        if not terms:
            return None
        result = self._request(self.search_url, params={
            'term': '+'.join(terms),
            'country': self.config['country'],
            'media': 'podcast',
            'entity': 'podcast',
            'attribute': ATTRIBUTES[attribute],
            'limit': limit,
            'explicit': self.config['explicit']
        })
        return [self._ref(item) for item in result.get('results', [])]

    def refresh(self, uri=None):
        try:
            self.genres = self._genres(self.config['root_genre_id'])
        except Exception as e:
            logger.error('Error retrieving genres from iTunes Store: %r', e)

    def _genres(self, id):
        result = self._request(self.genres_url, params={
            'id': id,
            'cc': self.config['country']
        })
        genres = result.get(str(id))
        self._charts(genres)  # preload
        return genres

    def _charts(self, genre):
        if '_charts' in genre:
            return genre['_charts'].get('results', [])
        result = self._request(self.charts_url, params={
            'g': genre['id'],
            'cc': self.config['country'],
            'name': self.config['browse_charts'],
            'limit': self.config['browse_limit']
        })
        charts = self._request(self.lookup_url, params={
            'id': ','.join(str(id) for id in result.get('resultIds', []))
        })
        genre['_charts'] = charts
        return charts.get('results', [])

    def _ref(self, item):
        return Ref.podcast(uri=item.get('feedUrl'), name=item.get('trackName'))

    def _request(self, url, params=None):
        timeout = self.config['timeout']
        response = self.session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        logger.debug('Retrieving %s took %s', response.url, response.elapsed)
        return response.json()
