import re
from urllib.parse import urljoin

from mopidy.models import Ref

import pytest
import responses
from mopidy_podcast_itunes import Extension


@pytest.fixture
def charts_url(config):
    return urljoin(config[Extension.ext_name]["base_url"], "/charts")


@pytest.fixture
def genres(charts_url):
    return {
        "26": {
            "name": "Podcasts",
            "id": "26",
            "chartUrls": {"podcasts": urljoin(charts_url, "?g=26")},
            "subgenres": {
                "1000": {
                    "name": "Foo",
                    "id": "1000",
                    "chartUrls": {"podcasts": urljoin(charts_url, "?g=1000")},
                },
                "1001": {
                    "name": "Bar",
                    "id": "1001",
                    "chartUrls": {"podcasts": urljoin(charts_url, "?g=1001")},
                    "subgenres": {
                        "1002": {
                            "name": "Baz",
                            "id": "1002",
                            "chartUrls": {
                                "podcasts": urljoin(charts_url, "?g=1002")
                            },
                        }
                    },
                },
            },
        }
    }


@pytest.fixture
def charts():
    return {"resultIds": [1234, 5678]}


@pytest.fixture
def lookup():
    return {
        "resultCount": 2,
        "results": [
            {
                "kind": "podcast",
                "collectionName": "foo",
                "collectionId": 1234,
                "feedUrl": "http://example.com/1234",
                "trackName": "foo",
                "trackId": 1234,
            },
            {
                "kind": "podcast",
                "collectionName": "bar",
                "collectionId": 5678,
                "feedUrl": "http://example.com/5678",
                "trackName": "bar",
                "trackId": 5678,
            },
        ],
    }


def test_root_directory(config, library):
    assert library.root_directory.uri == "podcast+itunes:"


@responses.activate
def test_browse_root(config, library, genres):
    responses.add(responses.GET, re.compile(r".*/genres\b.*"), json=genres)
    assert library.browse("podcast+itunes:") == [
        Ref.directory(name="Top Podcasts", uri="podcast+itunes:charts:26"),
        Ref.directory(name="Bar", uri="podcast+itunes:genre:1001"),
        Ref.directory(name="Foo", uri="podcast+itunes:charts:1000"),
    ]


@responses.activate
def test_browse_charts(config, library, genres, charts, lookup):
    responses.add(responses.GET, re.compile(r".*/genres\b.*"), json=genres)
    responses.add(responses.GET, re.compile(r".*/charts\b.*"), json=charts)
    responses.add(responses.GET, re.compile(r".*/lookup\b.*"), json=lookup)
    assert library.browse("podcast+itunes:charts:1000") == [
        Ref.album(name="foo", uri="podcast+http://example.com/1234"),
        Ref.album(name="bar", uri="podcast+http://example.com/5678"),
    ]


@responses.activate
def test_browse_subgenre(config, library, genres, charts, lookup):
    responses.add(responses.GET, re.compile(r".*/genres\b.*"), json=genres)
    responses.add(responses.GET, re.compile(r".*/charts\b.*"), json=charts)
    responses.add(responses.GET, re.compile(r".*/lookup\b.*"), json=lookup)
    assert library.browse("podcast+itunes:genre:1001") == [
        Ref.directory(name="Top Bar", uri="podcast+itunes:charts:1001"),
        Ref.directory(name="Baz", uri="podcast+itunes:charts:1002"),
    ]
