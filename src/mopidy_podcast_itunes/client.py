import logging
from functools import reduce
from urllib.parse import urljoin

from . import Extension

BASE_URL = "http://itunes.apple.com/"
GENRES_PATH = "/WebObjects/MZStoreServices.woa/ws/genres"
LOOKUP_PATH = "/lookup"
SEARCH_PATH = "/search"

logger = logging.getLogger(__name__)


def genres(result, g):
    result.update(reduce(genres, g.get("subgenres", {}).values(), {}))
    result[g["id"]] = g
    return result


def http_adapter(config):
    import requests

    return requests.adapters.HTTPAdapter(
        max_retries=config[Extension.ext_name]["retries"]
    )


class iTunesPodcastClient:
    def __init__(self, config):
        self.__base_url = config[Extension.ext_name]["base_url"]
        self.__country = config[Extension.ext_name]["country"]
        self.__timeout = config[Extension.ext_name]["timeout"]
        self.__session = Extension.get_requests_session(config)
        self.__session.mount(self.__base_url, http_adapter(config))
        self.__genres = {}

    def charts(self, genre_id, name, limit=None):
        g = self.genre(genre_id)
        try:
            url = g["chartUrls"][name]
        except KeyError:
            raise LookupError(f"No {name} charts for genreId {genre_id}")
        ids = self.__request(url, params={"limit": limit}).get("resultIds", [])
        result = self.__request(
            urljoin(self.__base_url, LOOKUP_PATH),
            params={"id": ",".join(map(str, ids))},
        )
        return result.get("results", [])

    def genre(self, genre_id):
        if genre_id not in self.__genres:
            g = self.__request(
                urljoin(self.__base_url, GENRES_PATH),
                params={"id": genre_id, "cc": self.__country},
            )
            self.__genres.update(reduce(genres, g.values(), {}))
        return self.__genres[genre_id]

    def refresh(self):
        self.__genres = {}

    def search(
        self,
        term,
        media=None,
        entity=None,
        attribute=None,
        limit=None,
        explicit=None,
        genre_id=None,
    ):
        result = self.__request(
            urljoin(self.__base_url, SEARCH_PATH),
            params={
                "term": term,
                "country": self.__country,
                "media": media,
                "entity": entity,
                "attribute": attribute,
                "limit": limit,
                # apparently only lowercase will work, contrary to iTunes specs
                "explicit": (explicit.lower() if explicit else None),
                # undocumented, and apparently not really working as expected
                "genreId": genre_id,
            },
        )
        return result.get("results", [])

    def __request(self, url, **kwargs):
        response = self.__session.get(url, timeout=self.__timeout, **kwargs)
        response.raise_for_status()
        logger.debug("Retrieving %s took %s", response.url, response.elapsed)
        return response.json()


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import logging
    import json
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("arg", metavar="TERM | CHARTS", nargs="?")
    parser.add_argument("-B", "--base-url", default=BASE_URL)
    parser.add_argument("-a", "--attribute")
    parser.add_argument("-c", "--country", default="US")
    parser.add_argument("-e", "--entity")
    parser.add_argument("-g", "--genre-id")
    parser.add_argument("-i", "--indent", type=int)
    parser.add_argument("-l", "--limit", type=int)
    parser.add_argument("-m", "--media")
    parser.add_argument("-r", "--retries", type=int, default=0)
    parser.add_argument("-t", "--timeout", type=float)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-x", "--explicit")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARN)

    client = iTunesPodcastClient(
        {
            Extension.ext_name: {
                "base_url": args.base_url,
                "country": args.country,
                "timeout": args.timeout,
                "retries": args.retries,
            },
            "proxy": {},
        }
    )

    if not args.arg:
        result = client.genre(args.genre_id or "26")
    elif args.arg in ("podcasts", "audioPodcasts", "videoPodcasts"):
        result = client.charts(args.genre_id or "26", args.arg, args.limit)
    else:
        result = client.search(
            args.arg,
            args.media,
            args.entity,
            args.attribute,
            args.limit,
            args.explicit,
            args.genre_id,
        )
    json.dump(result, sys.stdout, indent=args.indent, sort_keys=True)
    sys.stdout.write("\n")
