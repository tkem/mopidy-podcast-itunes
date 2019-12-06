from mopidy import models

import pytest
from mopidy_podcast_itunes import translator


@pytest.mark.parametrize(
    "feedurl,guid,expected",
    [
        (
            "http://example.com/feed.xml",
            None,
            "podcast+http://example.com/feed.xml",
        ),
        (
            "http://example.com/feed.xml",
            "1",
            "podcast+http://example.com/feed.xml#1",
        ),
    ],
)
def test_uri(feedurl, guid, expected):
    assert translator.uri(feedurl, guid) == expected


@pytest.mark.parametrize(
    "item,expected",
    [
        (
            {
                "kind": "podcast",
                "feedUrl": "http://example.com/feed",
                "collectionName": "bar",
                "trackName": "foo",
            },
            models.Ref.album(uri="podcast+http://example.com/feed", name="bar"),
        ),
        (
            {
                "kind": "podcast-episode",
                "feedUrl": "http://example.com/feed",
                "collectionName": "bar",
                "episodeGuid": "1",
                "trackName": "foo",
            },
            models.Ref.track(
                uri="podcast+http://example.com/feed#1", name="foo"
            ),
        ),
    ],
)
def test_ref(item, expected):
    assert translator.ref(item) == expected


@pytest.mark.parametrize(
    "item",
    [
        {},
        {"kind": "song", "trackName": "foo"},
        {"kind": "podcast", "trackName": "foo"},
        {"kind": "podcast-episode", "trackId": 1234, "trackName": "foo"},
    ],
)
def test_ref_error(item):
    # TODO: raise ValueError for all of these
    with pytest.raises(Exception):
        translator.ref(item)


@pytest.mark.parametrize(
    "item,expected",
    [
        (
            {
                "kind": "podcast",
                "feedUrl": "http://example.com/feed",
                "collectionName": "bar",
                "trackName": "foo",
                "artistName": "baz",
                "releaseDate": "1972-09-16T16:55:00Z",
            },
            models.Album(
                uri="podcast+http://example.com/feed",
                name="bar",
                artists=[models.Artist(name="baz")],
                date="1972-09-16",
            ),
        ),
        (
            {
                "kind": "podcast-episode",
                "feedUrl": "http://example.com/feed",
                "collectionName": "bar",
                "episodeGuid": "1",
                "trackName": "foo",
                "artistName": "baz",
                "primaryGenreName": "Music",
                "releaseDate": "1972-09-16T16:55:00Z",
                "trackTimeMillis": 3600,
            },
            models.Track(
                uri="podcast+http://example.com/feed#1",
                name="foo",
                album=models.Album(
                    uri="podcast+http://example.com/feed", name="bar"
                ),
                artists=[models.Artist(name="baz")],
                date="1972-09-16",
                genre="Music",
                length=3600,
            ),
        ),
    ],
)
def test_model(item, expected):
    assert translator.model(item) == expected


@pytest.mark.parametrize(
    "item",
    [
        {},
        {"kind": "song", "trackName": "foo"},
        {"kind": "podcast", "trackName": "foo"},
        {"kind": "podcast-episode", "trackName": "foo", "trackId": 12345678},
        {
            "kind": "podcast-episode",
            "trackName": "foo",
            "collectionId": 12345678,
        },
    ],
)
def test_model_error(item):
    # TODO: raise ValueError for all of these
    with pytest.raises(Exception):
        translator.model(item)


@pytest.mark.parametrize(
    "query,expected",
    [
        (
            {"any": ["foo"]},
            {
                "term": "foo",
                "media": "podcast",
                "entity": "podcast,podcastEpisode",
                "attribute": None,
                # 'genre_id': None
            },
        ),
        (
            {"album": ["foo", "bar"]},
            {
                "term": "foo bar",
                "media": "podcast",
                "entity": "podcast",
                "attribute": "titleTerm",
                # 'genre_id': None
            },
        ),
        (
            {"genre": ["Music"]},
            {
                "term": "Music",
                "media": "podcast",
                "entity": "podcast,podcastEpisode",
                "attribute": "genreTerm",
                # 'genre_id': None
            },
        ),
    ],
)
def test_query(query, expected):
    assert translator.query(query) == expected
