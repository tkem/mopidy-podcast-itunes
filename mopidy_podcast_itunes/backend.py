import pykka
from mopidy import backend

from .client import iTunesPodcastClient
from .library import iTunesPodcastLibraryProvider


class iTunesPodcastBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = ["podcast+itunes"]

    def __init__(self, config, audio):
        super().__init__()
        self.client = iTunesPodcastClient(config)
        self.library = iTunesPodcastLibraryProvider(config, self)
