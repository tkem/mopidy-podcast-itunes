import re

from mopidy.models import Ref

import pytest

import responses


@pytest.fixture
def genres():
    return {
        "26": {
            "name": "Podcasts",
            "id": "26",
            "subgenres": {
                "1000": {
                    "name": "Foo",
                    "id": "1000",
                },
                "1001": {
                    "name": "Bar",
                    "id": "1001",
                    "subgenres": {
                        "1002": {
                            "name": "Baz",
                            "id": "1002",
                        }
                    },
                },
            },
        }
    }


@pytest.fixture
def toppodcasts():
    return {
        "feed": {
            "author": {
                "name": {"label": "iTunes Store"},
                "uri": {"label": "http://www.apple.com/itunes/"},
            },
            "entry": [
                {
                    "id": {
                        "attributes": {"im:id": "1234"},
                    },
                },
                {
                    "id": {
                        "attributes": {"im:id": "5678"},
                    },
                },
            ],
        }
    }


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
def test_browse_charts(config, library, genres, toppodcasts, lookup):
    responses.add(responses.GET, re.compile(r".*/genres\b.*"), json=genres)
    responses.add(responses.GET, re.compile(r".*/toppodcasts\b.*"), json=toppodcasts)
    responses.add(responses.GET, re.compile(r".*/lookup\b.*"), json=lookup)
    assert library.browse("podcast+itunes:charts:1000") == [
        Ref.album(name="foo", uri="podcast+http://example.com/1234"),
        Ref.album(name="bar", uri="podcast+http://example.com/5678"),
    ]


@responses.activate
def test_browse_subgenre(config, library, genres, toppodcasts, lookup):
    responses.add(responses.GET, re.compile(r".*/genres\b.*"), json=genres)
    responses.add(responses.GET, re.compile(r".*/toppodcasts\b.*"), json=toppodcasts)
    responses.add(responses.GET, re.compile(r".*/lookup\b.*"), json=lookup)
    assert library.browse("podcast+itunes:genre:1001") == [
        Ref.directory(name="Top Bar", uri="podcast+itunes:charts:1001"),
        Ref.directory(name="Baz", uri="podcast+itunes:charts:1002"),
    ]
