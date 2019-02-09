from __future__ import unicode_literals

import logging
import math
import os.path
import time

from mopidy import __version__ as mopidy_version

from requests import Request, Session, exceptions
from requests.adapters import HTTPAdapter

from mopidy_dirble import __version__ as dirble_version

logger = logging.getLogger(__name__)

def _normalize_keys(data):
    return {k.lower(): v for k, v in data.items()}


def _paginate(fetch, offset, limit, page_size):
    result = []
    page = int(math.floor((offset) / float(page_size)))
    discard = offset - page * page_size

    while len(result) < limit + 1:
        tmp = fetch(page)
        if not tmp:
            break
        result.extend(tmp[discard:])
        page += 1
        discard = 0

    return result[:limit], len(result) > limit


class Dirble(object):
    """Light wrapper for Dirble API lookup.

    Important things to note:
    - The client will retry up to three times before giving up for network
      errors etc.
    - The client will do exponential back off when requests fail or timeout.
    - The client will cache results aggressively.
    - Failed requests will return an empty default type appropriate for the
      lookup in question, normally a empty dict or list.
    - The data returned comes direct from the API's JSON.
    - The data is not copied, so beware of modifying what you get back.
    """

    def __init__(self, api_key, timeout):
        self._cache = {}
        self._stations = {}
        self._countries = {}
        self._invalid_token = False
        self._timeout = timeout / 1000.0
        self._backoff_until = time.time()
        self._backoff_max = 60
        self._backoff = 1

        self._base_uri = 'https://api.dirble.com/v2/'

        self._session = Session()
        self._session.params = {'token': api_key}
        self._session.headers['User-Agent'] = ' '.join([
            'Mopidy-Dirble/%s' % dirble_version,
            'Mopidy/%s' % mopidy_version,
            self._session.headers['User-Agent']])
        self._session.mount(self._base_uri, HTTPAdapter(max_retries=3))

    def flush(self):
        self._cache = {}
        self._stations = {}
        self._countries = {}
        self._invalid_token = False

    def categories(self):
        return self._fetch('categories/tree', [])

    def category(self, identifier):
        identifier = int(identifier)
        categories = self.categories()[:]
        while categories:
            c = categories.pop(0)
            if c['id'] == identifier:
                return c
            categories.extend(c['children'])
        return None

    def subcategories(self, identifier):
        category = self.category(identifier)
        return (category or {}).get('children', [])

    def stations(self, category=None, country=None, offset=None, limit=None):
        if category and not country:
            path = 'category/%s/stations' % category
        elif country and not category:
            path = 'countries/%s/stations' % country.lower()
        else:
            return []

        def fetch(page):
            return self._fetch(path, [], {'page': page, 'per_page': 30})

        stations, has_more = _paginate(fetch, offset or 0, limit or 50, 30)
        for station in stations:
            self._stations.setdefault(station['id'], station)
        return stations

    def station(self, identifier):
        identifier = int(identifier)  # Ensure we are consistent for cache key.
        if identifier in self._stations:
            return self._stations[identifier]
        station = self._fetch('station/%s' % identifier, {})
        if station:
            if 'id' not in station:
                station['id'] = identifier
            self._stations.setdefault(station['id'], station)
        return station

    def continents(self):
        return self._fetch('continents', [])

    def countries(self, continent=None):
        if continent:
            return self._fetch('continents/%s/countries' % continent, [])
        else:
            return self._fetch('countries', [])

    def country(self, country_code):
        if not self._countries:
            for c in self.countries():
                self._countries[c['country_code'].lower()] = c
        return self._countries.get(country_code.lower())

    # TODO: support category and country filter + pagination.
    def search(self, query):
        stations = self._fetch('search', [], {'query': query}, 'POST')
        for station in stations:
            self._stations.setdefault(station['id'], station)
        return stations

    def _fetch(self, path, default, params=None, method='GET'):
        # Give up right away if we know the token is bad.
        if self._invalid_token:
            return default

        request = Request(
            method, os.path.join(self._base_uri, path), params=params)
        prepared = self._session.prepare_request(request)

        # Try and serve request from our cache.
        if prepared.url in self._cache:
            logger.debug('Cache hit: %s', prepared.url)
            return self._cache[prepared.url]

        # Check if we should back of sending queries.
        if time.time() < self._backoff_until:
            logger.debug('Back off fallback used: %s', uri)
            return default

        try:
            logger.debug('Fetching: %s', prepared.url)
            resp = self._session.send(prepared, timeout=self._timeout)

            # Get succeeded, convert JSON, normalize and return.
            if resp.status_code == 200:
                data = resp.json(object_hook=_normalize_keys)
                self._cache[prepared.url] = data
                self._backoff = 1
                return data

            # Special case invalid tokens as there is no point in doing any
            # further requests.
            if resp.status_code == 401:
                logger.error('Dirble API token is not valid, please double '
                             'check your key or get a new one at dirble.com')
                self._invalid_token = True
                return default

            # Don't treat a 404 as an error, just fallback to default value.
            if resp.status_code == 404:
                return default

            # Anything else is an error.
            resp.raise_for_status()

        except exceptions.RequestException as e:
            logger.warning('Fetching Dirble data failed: %s', e)
        except ValueError as e:
            logger.warning('Decoding Dirble data failed: %s', e)

        # If we made it this far something is broken on our side or with the
        # service, so start backing off sending requests.
        self._backoff = min(self._backoff_max, self._backoff*2)
        self._backoff_until = time.time() + self._backoff
        logger.debug('Entering back off mode for %d seconds.', self._backoff)
        return default
