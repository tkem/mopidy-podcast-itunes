from __future__ import unicode_literals

import collections
import logging

from mopidy import backend, models

import uritools

from . import Extension, translator

GENRES_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'
LOOKUP_PATH = '/lookup'
SEARCH_PATH = '/search'

logger = logging.getLogger(__name__)


class iTunesPodcastLibraryProvider(backend.LibraryProvider):

    root_directory = models.Ref.directory(
        uri='podcast+itunes:', name='iTunes Podcasts'
    )

    def __init__(self, config, backend):
        super(iTunesPodcastLibraryProvider, self).__init__(backend)
        self.__session = Extension.get_requests_session(config)

        ext_config = config[Extension.ext_name]
        self.__country = ext_config['country']
        self.__explicit = ext_config['explicit']
        self.__charts_type = ext_config['charts_type']
        self.__charts_limit = ext_config['charts_limit']
        self.__search_limit = ext_config['search_limit']
        self.__root_genre_id = ext_config['root_genre_id']
        self.__timeout = ext_config['timeout']

        base_url = ext_config['base_url']
        self.__genres_url = uritools.urijoin(base_url, GENRES_PATH)
        self.__lookup_url = uritools.urijoin(base_url, LOOKUP_PATH)
        self.__search_url = uritools.urijoin(base_url, SEARCH_PATH)

        self.__root_genres = {}  # cached genre map

    def browse(self, uri):
        if self.__root_genres:
            g = self.__root_genres
        else:
            self.__root_genres = g = self.__genres(self.__root_genre_id)
        for pseg in uritools.urisplit(uri).path.split('/')[1:]:
            if not pseg:
                g = dict(g, subgenres=None)
            elif pseg in g.get('subgenres', {}):
                g = g['subgenres'][pseg]
            else:
                logger.warning('Invalid %s URI %s', Extension.ext_name, uri)
        if g.get('subgenres') is None:
            return list(self.__charts(g))
        else:
            return list(self.__browse(uri + '/', g))

    def refresh(self, uri=None):
        self.__root_genres = {}

    def search(self, query=None, uris=None, exact=False):
        try:
            query = translator.query(query or {}, uris or [], exact)
        except NotImplementedError as e:
            logger.info('Not searching %s: %s', Extension.dist_name, e)
            return None
        search = self.__request(self.__search_url, params=dict(
            query,
            country=self.__country,
            explicit=self.__explicit,
            limit=self.__search_limit
        ))
        results = collections.defaultdict(list)
        for result in search.get('results', []):
            try:
                model = translator.model(result)
            except Exception as e:
                logger.error('Error converting iTunes search result: %s', e)
            else:
                results[type(model)].append(model)
        return models.SearchResult(
            albums=results[models.Album],
            artists=results[models.Artist],
            tracks=results[models.Track]
        )

    def __browse(self, uri, g, key=lambda g: g['name'].lower()):
        yield models.Ref.directory(uri=uri, name='Top '+g['name'])
        for subg in sorted(g['subgenres'].values(), key=key):
            yield models.Ref.directory(uri=uri+subg['id'], name=subg['name'])

    def __charts(self, g):
        charts = self.__request(g['chartUrls'][self.__charts_type], params={
            # TODO: no "explicit" parameter for chartUrls?
            'limit': self.__charts_limit
        })
        lookup = self.__request(self.__lookup_url, params={
            'id': ','.join(map(str, charts.get('resultIds', [])))
        })
        for result in lookup.get('results', []):
            try:
                ref = translator.ref(result)
            except Exception as e:
                logger.error('Error converting iTunes search result: %s', e)
            else:
                yield ref

    def __genres(self, id):
        genres = self.__request(self.__genres_url, params={
            'cc': self.__country,
            'id': id
        })
        return genres.get(id, {})

    def __request(self, url, **kwargs):
        response = self.__session.get(url, timeout=self.__timeout, **kwargs)
        response.raise_for_status()
        logger.debug('Retrieving %s took %s', response.url, response.elapsed)
        return response.json()
