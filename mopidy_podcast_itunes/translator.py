import uritools
from mopidy import models

from . import Extension

_MODELS = {
    "podcast": lambda item: models.Album(
        uri=uri(item["feedUrl"]),
        name=item.get("collectionName", item["trackName"]),
        artists=artists(item),
        date=(item.get("releaseDate", "").partition("T")[0] or None),
        num_tracks=item.get("trackCount"),
    ),
    "podcast-episode": lambda item: models.Track(
        uri=uri(item["feedUrl"], item["episodeGuid"]),
        name=item["trackName"],
        album=models.Album(
            uri=uri(item["feedUrl"]), name=item["collectionName"]
        ),
        artists=artists(item),
        date=(item.get("releaseDate", "").partition("T")[0] or None),
        genre=item.get("primaryGenreName"),
        length=item.get("trackTimeMillis"),
        comment=item.get("description"),
    ),
}

_REFS = {
    "podcast": lambda item: models.Ref.album(
        uri=uri(item["feedUrl"]),
        name=item.get("collectionName", item["trackName"]),
    ),
    "podcast-episode": lambda item: models.Ref.track(
        uri=uri(item["feedUrl"], item["episodeGuid"]), name=item["trackName"]
    ),
}

# FIXME: 'authorTerm' and 'titleTerm' not working properly for podcastEpisode
_QUERY = {
    "track_name": ("podcastEpisode", "titleTerm"),
    "any": ("podcast,podcastEpisode", None),
    "album": ("podcast", "titleTerm"),
    "albumartist": ("podcast", "authorTerm"),
    "artist": ("podcast,podcastEpisode", "authorTerm"),
    "genre": ("podcast,podcastEpisode", "genreTerm"),
    "comment": ("podcastEpisode", "descriptionTerm"),
}


_SCHEME = Extension.ext_name.replace("-", "+")


def artists(item):
    if "artistName" in item:
        return [models.Artist(name=item["artistName"])]
    else:
        return None


def directory(type, g, name=None, scheme=_SCHEME):
    return models.Ref.directory(
        uri=":".join((scheme, type, g["id"])), name=(name or g["name"])
    )


def model(item):
    try:
        translate = _MODELS[item["kind"]]
    except KeyError:
        raise TypeError('Unsupported result type "%s"' % item.get("kind"))
    else:
        return translate(item)


def query(query, uris=tuple(), exact=False):
    if exact:
        raise NotImplementedError("Exact queries not supported")
    try:
        ((key, values),) = query.items()
    except ValueError:
        raise NotImplementedError("Multi-key queries not supported")
    try:
        entity, attribute = _QUERY[key]
    except KeyError:
        raise NotImplementedError('Search key "%s" not supported' % key)
    return {
        "term": " ".join(values),
        "media": "podcast",
        "entity": entity,
        "attribute": attribute,
        # FIXME: not working as expected...
        # 'genre_id': ','.join(uri.rpartition(':')[2] for uri in uris) or None
    }


def ref(item):
    try:
        translate = _REFS[item["kind"]]
    except KeyError:
        raise ValueError('Unsupported result type "%s"' % item.get("kind"))
    else:
        return translate(item)


def uri(feedurl, guid=None, safe=uritools.SUB_DELIMS + ":@/?"):
    uri = uritools.uridefrag("podcast+" + feedurl).uri
    if guid:
        return uri + "#" + uritools.uriencode(guid, safe=safe).decode()
    else:
        return uri
