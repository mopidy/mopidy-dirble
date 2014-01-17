from __future__ import unicode_literals

import re

from mopidy.models import Ref


def unparse_uri(variant, identifier):
    return b'dirble:%s:%s' % (variant, identifier)


def parse_uri(uri):
    result = re.findall(r'^dirble:([a-z]+)(?::(\d+))?$', uri)
    if result:
        return result[0]
    return None, None


def station_to_ref(station):
    name = station.get('name', station['streamurl']).strip()
    country = station.get('country', '??')
    uri = unparse_uri(b'station', station['id'])
    return Ref.track(uri=uri, name='%s - %s' % (country, name))


def category_to_ref(category, primary=True):
    if primary:
        uri = unparse_uri(b'category', category['id'])
    else:
        uri = unparse_uri(b'subcategory', category['id'])
    return Ref.directory(uri=uri, name=category.get('name', uri))
