# References:
# noqa http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html
# noqa http://www.apple.com/itunes/affiliates/resources/documentation/genre-mapping.html

from __future__ import unicode_literals

import logging
import requests

from urlparse import urljoin

from mopidy_podcast import PodcastDirectory
from mopidy_podcast.models import Ref

# TODO: load dynamically at startup
GENRES = {
    26: 'Podcasts',
    1301: 'Arts',
    1302: 'Personal Journals',
    1303: 'Comedy',
    1304: 'Education',
    1305: 'Kids & Family',
    1306: 'Food',
    1307: 'Health',
    1309: 'TV & Film',
    1310: 'Music',
    1311: 'News & Politics',
    1314: 'Religion & Spirituality',
    1315: 'Science & Medicine',
    1316: 'Sports & Recreation',
    1318: 'Technology',
    1320: 'Places & Travel',
    1321: 'Business',
    1323: 'Games & Hobbies',
    1324: 'Society & Culture',
    1325: 'Government & Organizations',
    1401: 'Literature',
    1402: 'Design',
    1404: 'Video Games',
    1405: 'Performing Arts',
    1406: 'Visual Arts',
    1410: 'Careers',
    1412: 'Investing',
    1413: 'Management & Marketing',
    1415: 'K-12',
    1416: 'Higher Education',
    1417: 'Fitness & Nutrition',
    1420: 'Self-Help',
    1421: 'Sexuality',
    1438: 'Buddhism',
    1439: 'Christianity',
    1440: 'Islam',
    1441: 'Judaism',
    1443: 'Philosophy',
    1444: 'Spirituality',
    1446: 'Gadgets',
    1448: 'Tech News',
    1450: 'Podcasting',
    1454: 'Automotive',
    1455: 'Aviation',
    1456: 'Outdoor',
    1459: 'Fashion & Beauty',
    1460: 'Hobbies',
    1461: 'Other Games',
    1462: 'History',
    1463: 'Hinduism',
    1464: 'Other',
    1465: 'Professional',
    1466: 'College & High School',
    1467: 'Amateur',
    1468: 'Educational Technology',
    1469: 'Language Courses',
    1470: 'Training',
    1471: 'Business News',
    1472: 'Shopping',
    1473: 'National',
    1474: 'Regional',
    1475: 'Local',
    1476: 'Non-Profit',
    1477: 'Natural Sciences',
    1478: 'Medicine',
    1479: 'Social Sciences',
    1480: 'Software How-To',
    1481: 'Alternative Health',
}

SUBGENRES = {
    26: [
        1301, 1303, 1304, 1305, 1307, 1309, 1310, 1311, 1314, 1315, 1316, 1318,
        1321, 1323, 1324, 1325
    ],
    1301: [1306, 1401, 1402, 1405, 1406, 1459],
    1304: [1415, 1416, 1468, 1469, 1470],
    1307: [1417, 1420, 1421, 1481],
    1314: [1438, 1439, 1440, 1441, 1444, 1463, 1464],
    1315: [1477, 1478, 1479],
    1316: [1456, 1465, 1466, 1467],
    1318: [1446, 1448, 1450, 1480],
    1321: [1410, 1412, 1413, 1471, 1472],
    1323: [1404, 1454, 1455, 1460, 1461],
    1324: [1302, 1320, 1443, 1462],
    1325: [1473, 1474, 1475, 1476],
}

ATTRIBUTES = {
    PodcastDirectory.AUTHOR: 'authorTerm',
    PodcastDirectory.CATEGORY: None,  # TODO
    PodcastDirectory.DESCRIPTION: 'descriptionTerm',
    PodcastDirectory.KEYWORDS: 'keywordsTerm',
    PodcastDirectory.TITLE: 'titleTerm',
}

SEARCH_PATH = '/search'
BROWSE_PATH = '/WebObjects/MZStoreServices.woa/ws/genres'

logger = logging.getLogger(__name__)


class iTunesDirectory(PodcastDirectory):

    name = 'itunes'

    def __init__(self, backend):
        super(iTunesDirectory, self).__init__(backend)
        self.label = self.config['label']
        self.search_url = urljoin(self.config['base_url'], SEARCH_PATH)
        self.browse_url = urljoin(self.config['base_url'], BROWSE_PATH)
        self.session = requests.Session()

    @property
    def config(self):
        return self.backend.config['podcast-itunes']

    def browse(self, path):
        genre = int(path.lstrip('/') or 26)
        logger.info('Browse genre: %d', genre)
        if genre not in SUBGENRES:
            return []
        refs = []
        for id in SUBGENRES[genre]:
            logger.info('Subgenre: %d', id)
            ref = Ref.directory(uri='/%d' % id, name=GENRES[id])
            refs.append(ref)
        logger.info('Browse refs: %r', refs)
        return refs

    def search(self, terms=None, attribute=None):
        if not terms:
            return []
        response = self.session.get(self.search_url, params={
            'term': '+'.join(terms),
            'country': self.config['country'],
            'media': 'podcast',
            'entity': 'podcast',
            'attribute': ATTRIBUTES[attribute] if attribute else None,
            'limit': self.config['limit'],
            'explicit': self.config['explicit']
        }, timeout=self.config['timeout'])

        refs = []
        for result in response.json().get('results', []):
            trackId = result.get('trackId', 'n/a')
            if 'feedUrl' not in result:
                logger.warn('Missing feedUrl for iTunes trackId %s', trackId)
                continue
            name = result.get('trackName', 'iTunes trackId %s' % trackId)
            refs.append(Ref.podcast(uri=result['feedUrl'], name=name))
        return refs
