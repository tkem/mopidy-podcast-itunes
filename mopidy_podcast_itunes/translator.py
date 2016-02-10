from __future__ import unicode_literals

from mopidy import models

import uritools

_MODELS = {
    'podcast': lambda item: models.Album(
        uri=uri(item['feedUrl']),
        name=item.get('collectionName', item['trackName']),
        artists=(
            [models.Artist(name=item['artistName'])]
            if 'artistName' in item
            else None
        ),
        date=(item.get('releaseDate', '').partition('T')[0] or None),
        num_tracks=item.get('trackCount')
     ),
    'podcast-episode': lambda item: models.Track(
        uri=uri(item['feedUrl'], item['episodeGuid']),
        name=item['trackName'],
        album=models.Album(
            uri=uri(item['feedUrl']),
            name=item['collectionName']
        ),
        artists=(
            [models.Artist(name=item['artistName'])]
            if 'artistName' in item
            else None
        ),
        date=(item.get('releaseDate', '').partition('T')[0] or None),
        comment=item.get('description')
     )
}


_REFS = {
    'podcast': lambda item: models.Ref.album(
        name=item.get('collectionName', item['trackName']),
        uri=uri(item['feedUrl'])
     ),
    'podcast-episode': lambda item: models.Ref.track(
        name=item['trackName'],
        uri=uri(item['feedUrl'], item.get('episodeGuid'))
     )
}

# TODO: 'authorTerm' and 'titleTerm' not working properly for podcastEpisode
_QUERY = {
    'track_name': ('podcastEpisode', 'titleTerm'),
    'any': ('podcast,podcastEpisode', None),
    'album': ('podcast', 'titleTerm'),
    'albumartist': ('podcast', 'authorTerm'),
    'artist': ('podcast,podcastEpisode', 'authorTerm'),
    'genre': ('podcast,podcastEpisode', 'genreTerm'),
    'comment': ('podcastEpisode', 'descriptionTerm')
}


def model(result):
    try:
        translate = _MODELS[result['kind']]
    except KeyError:
        raise ValueError('Unsupported result type "%s"' % result.get('kind'))
    else:
        return translate(result)


def query(query, uris, exact):
    if exact:
        raise NotImplementedError('Exact queries not supported')
    try:
        uri, = uris
    except ValueError:
        raise NotImplementedError('Multi-path queries not supported')
    try:
        (key, values), = query.items()
    except ValueError:
        raise NotImplementedError('Only single-key queries supported')
    try:
        entity, attribute = _QUERY[key]
    except KeyError:
        raise NotImplementedError('Search key "%s" not supported' % key)
    return {
        'media': 'podcast',
        'term': ' '.join(values),
        'entity': entity,
        'attribute': attribute,
        'genreId': uritools.urisplit(uri).path.rpartition('/')[2] or None
    }


def ref(result):
    try:
        translate = _REFS[result['kind']]
    except KeyError:
        raise ValueError('Unsupported result type "%s"' % result.get('kind'))
    else:
        return translate(result)


def uri(feedurl, guid=None, safe=uritools.SUB_DELIMS+b':@/?'):
    uri, _ = uritools.uridefrag('podcast+' + feedurl)
    if guid is None:
        return uri
    else:
        return uri + '#' + uritools.uriencode(guid, safe=safe)
