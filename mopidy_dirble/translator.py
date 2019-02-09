from __future__ import unicode_literals

import collections
import re

from mopidy.models import Ref, Track


DirbleURI = collections.namedtuple(
    'DirbleURI', ['variant', 'identifier', 'offset'])


def unparse_uri(variant, identifier, offset=None):
    uri = b'dirble:%s:%s' % (variant, identifier)
    if offset is not None:
        uri += b':%s' % offset
    return uri


def parse_uri(uri):
    parts = uri.split(':')
    none = DirbleURI(None, None, None)

    if tuple(parts) == ('dirble', 'root'):
        return DirbleURI(parts[1], None, None)

    if len(parts) not in (3, 4):
        return none

    if parts[0] != 'dirble':
        return none

    if parts[1] in ('station', 'category', 'continent'):
        if not parts[2].isdigit():
            return none
    elif parts[1] in ('country'):
        if len(parts[2]) != 2 or not parts[2].isalpha():
            return none
    else:
        return none

    offset = None
    if len(parts) == 4:
        if parts[1] not in ('category', 'country'):
            return none
        if not parts[3].isdigit():
            return none
        offset = int(parts[3])

    return DirbleURI(parts[1], parts[2], offset)


def station_to_ref(station, show_country=True):
    name = station.get('name').strip()  # TODO: fallback to streams URI?
    if show_country:
        # TODO: make this a setting so users can set '$name [$country]' etc?
        name = '%s [%s]' % (name, station.get('country', '??'))
    uri = unparse_uri('station', station['id'])
    return Ref.track(uri=uri, name=name)


def station_to_track(station):
    ref = station_to_ref(station)
    return Track(uri=ref.uri, name=ref.name)


def category_to_ref(category):
    uri = unparse_uri('category', category['id'])
    return Ref.directory(uri=uri, name=category.get('title', uri))


def continent_to_ref(continent):
    uri = unparse_uri('continent', continent['id'])
    return Ref.directory(uri=uri, name=continent['name'])


def country_to_ref(country):
    uri = unparse_uri('country', country['country_code'].lower())
    return Ref.directory(uri=uri, name=country['name'])
