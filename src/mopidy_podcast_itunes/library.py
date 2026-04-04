import collections
import logging

from mopidy import backend, models

from . import Extension, translator

ROOT_GENRE_ID = "26"  # "Podcasts"

logger = logging.getLogger(__name__)


class iTunesPodcastLibraryProvider(backend.LibraryProvider):
    def __init__(self, config, backend):
        super().__init__(backend)
        self.__charts_kwargs = {
            "name": config[Extension.ext_name]["charts"],
            "limit": config[Extension.ext_name]["charts_limit"],
        }
        self.__search_kwargs = {
            "explicit": config[Extension.ext_name]["explicit"],
            "limit": config[Extension.ext_name]["search_limit"],
        }

    @property
    def root_directory(self):
        return models.Ref.directory(
            name="iTunes Store: Podcasts", uri="podcast+itunes:"
        )

    def browse(self, uri):
        if uri == self.root_directory.uri:
            type, id = "genre", ROOT_GENRE_ID
        else:
            _, type, id = uri.split(":")
        if type == "charts":
            return self.__charts(id)
        elif type == "genre":
            return self.__genre(id)
        else:
            logger.error("Invalid browse URI: %s", uri)

    def refresh(self, uri=None):
        self.backend.client.refresh()

    def search(self, query=None, uris=None, exact=False):
        # sanitize uris - remove duplicates, root directory
        uris = frozenset(uris or []).difference([self.root_directory.uri])
        try:
            kwargs = translator.query(query or {}, uris, exact)
        except NotImplementedError:
            return None  # query not supported
        except Exception as e:
            logger.error("%s", e)
        else:
            kwargs.update(self.__search_kwargs)
        results = collections.defaultdict(list)
        for item in self.backend.client.search(**kwargs):
            try:
                model = translator.model(item)
            except Exception as e:
                logger.error("Error converting iTunes search result: %s", e)
            else:
                results[type(model)].append(model)
        return models.SearchResult(
            albums=results[models.Album],
            artists=results[models.Artist],
            tracks=results[models.Track],
        )

    def __charts(self, id):
        refs = []
        for item in self.backend.client.charts(id, **self.__charts_kwargs):
            try:
                ref = translator.ref(item)
            except Exception as e:
                logger.error("Error converting iTunes charts item: %s", e)
            else:
                refs.append(ref)
        return refs

    def __genre(self, id):
        def key(g):
            return g["name"].lower()

        g = self.backend.client.genre(id)
        refs = [translator.directory("charts", g, "Top %s" % g["name"])]
        for genre in sorted(g.get("subgenres", {}).values(), key=key):
            if "subgenres" in genre:
                refs.append(translator.directory("genre", genre))
            else:
                refs.append(translator.directory("charts", genre))
        return refs
