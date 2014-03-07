from __future__ import unicode_literals

import logging

from mopidy_podcast import PodcastDirectory
#from mopidy_podcast.models import Ref

logger = logging.getLogger(__name__)


class ITunesDirectory(PodcastDirectory):

    name = 'itunes'

    def __init__(self, config, cache=None):
        self.config = config['podcast-itunes']
        self.browse_label = self.config['browse_label']

    def browse(self, path):
        return []

    def search(self, terms=None, attribute=None):
        return []
