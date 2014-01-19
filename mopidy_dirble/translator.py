from __future__ import unicode_literals

import re

from mopidy.models import Ref

import pycountry


def unparse_uri(variant, identifier):
    return b'dirble:%s:%s' % (variant, identifier)


def parse_uri(uri):
    result = re.findall(r'^dirble:([a-z]+)(?::(\d+|[a-z]{2}))?$', uri)
    if result:
        return result[0]
    return None, None


def station_to_ref(station):
    name = station.get('name', station['streamurl']).strip()
    country = station.get('country', '??')
    uri = unparse_uri('station', station['id'])
    return Ref.track(uri=uri, name='%s - %s' % (country, name))


def category_to_ref(category):
    uri = unparse_uri('category', category['id'])
    return Ref.directory(uri=uri, name=category.get('name', uri))


def country_to_ref(country_code):
    uri = unparse_uri('country', country_code.lower())
    try:
        country = pycountry.countries.get(alpha2=country_code.upper())
        return Ref.directory(uri=uri, name=country.name)
    except KeyError:
        return Ref.directory(uri=uri, name=country_code.upper())
