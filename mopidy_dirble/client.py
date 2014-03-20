from __future__ import unicode_literals

import json
import logging
import time
import urllib2

logger = logging.getLogger(__name__)


class Dirble(object):
    """Light wrapper for Dirble API lookup.

    Important things to note:
    - The client will do exponential back off when requests fail or timeout.
    - The client will cache results aggressively.
    - Failed requests will return an empty default type appropriate for the
      lookup in question, normally a empty dict or list.
    - The data returned comes direct from the API's JSON.
    - For stations, only the minimal data set returned by station lists is
      guaranteed to be there.
    """
    def __init__(self, api_key, timeout):
        self._base_uri = 'http://api.dirble.com/v1/%s/apikey/' + api_key
        self._cache = {}
        self._stations = {}
        self._timeout = timeout / 1000.0
        self._backoff_until = time.time()
        self._backoff_max = 60
        self._backoff = 1

    def flush(self):
        self._cache = {}
        self._stations = {}

    def categories(self, category=None):
        if category:
            path = '/primaryid/%s' % category
            return self._fetch('childCategories', path, [])
        else:
            return self._fetch('primaryCategories', '', [])

    def stations(self, category=None, country=None):
        if category and not country:
            path = '/id/%s' % category
            stations = self._fetch('stations', path, [])
        elif country and not category:
            path = '/country/%s' % country.lower()
            stations = self._fetch('country', path, [])
        else:
            return []

        for station in stations:
            self._stations.setdefault(station['id'], station)
        return stations

    def station(self, identifier):
        identifier = int(identifier)  # Ensure we are consistent for cache key.
        if identifier in self._stations:
            return self._stations[identifier]
        path = '/id/%s' % identifier
        station = self._fetch('station', path, {})
        if station:
            self._stations.setdefault(station['id'], station)
        return station

    def _fetch(self, variant, path, default):
        uri = (self._base_uri % variant) + path
        if uri in self._cache:
            logger.debug('Cache hit: %s', uri)
            return self._cache[uri]

        if time.time() < self._backoff_until:
            logger.debug('Back off fallback used: %s', uri)
            return default

        logger.debug('Fetching: %s', uri)
        try:
            fp = urllib2.urlopen(uri, timeout=self._timeout)
            data = json.load(fp)
            self._cache[uri] = data
            self._backoff = 1
            return data
        except urllib2.HTTPError as e:
            logger.debug('Fetch failed, HTTP %s: %s', e.code, e.reason)
            if e.code == 404:
                self._cache[uri] = default
                return default
        except IOError as e:
            logger.debug('Fetch failed: %s', e)
        except ValueError as e:
            logger.warning('Fetch failed: %s', e)

        self._backoff = min(self._backoff_max, self._backoff*2)
        self._backoff_until = time.time() + self._backoff
        logger.debug('Entering back off mode for %d seconds.', self._backoff)
        return default
