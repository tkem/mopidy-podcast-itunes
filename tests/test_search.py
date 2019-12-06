import re

from mopidy import models

import pytest
import responses


@pytest.fixture
def results():
    return {
        "resultCount": 3,
        "results": [
            {
                "kind": "podcast",
                "collectionId": 1234,
                "collectionName": "Foo",
                "feedUrl": "http://example.com/feed1234",
                "trackId": 1234,
                "trackName": "Foo",
            },
            {
                "kind": "podcast-episode",
                "collectionId": 1234,
                "collectionName": "Foo",
                "episodeGuid": "5678",
                "feedUrl": "http://example.com/feed1234",
                "trackId": 5678,
                "trackName": "Bar",
            },
            {"kind": "song", "trackName": "Baz"},
        ],
    }


@responses.activate
def test_search(config, library, results):
    responses.add(responses.GET, re.compile(r".*/search\b.*"), json=results)
    assert library.search({"any": ["foo"]}) == models.SearchResult(
        albums=[
            models.Album(name="Foo", uri="podcast+http://example.com/feed1234")
        ],
        tracks=[
            models.Track(
                name="Bar",
                uri="podcast+http://example.com/feed1234#5678",
                album=models.Album(
                    name="Foo", uri="podcast+http://example.com/feed1234"
                ),
            )
        ],
    )
