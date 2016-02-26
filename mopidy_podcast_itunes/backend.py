from __future__ import unicode_literals

from mopidy import backend

import pykka

from .client import iTunesPodcastClient
from .library import iTunesPodcastLibraryProvider


class iTunesPodcastBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = ['podcast+itunes']

    def __init__(self, config, audio):
        super(iTunesPodcastBackend, self).__init__()
        self.client = iTunesPodcastClient(config)
        self.library = iTunesPodcastLibraryProvider(config, self)
