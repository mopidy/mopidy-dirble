from __future__ import unicode_literals

import re

from mopidy.models import Ref, Track


def unparse_uri(variant, identifier):
    return b'dirble:%s:%s' % (variant, identifier)


def parse_uri(uri):
    result = re.findall(r'^dirble:([a-z]+)(?::(\d+|[a-z]{2}))?$', uri)
    if result:
        return result[0]
    return None, None


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
