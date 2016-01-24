from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Image, Ref, SearchResult

import pykka

from . import client, translator

logger = logging.getLogger(__name__)


class DirbleBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = ['dirble']

    def __init__(self, config, audio):
        super(DirbleBackend, self).__init__()
        self.dirble = client.Dirble(config['dirble']['api_key'],
                                    config['dirble']['timeout'])
        self.countries = config['dirble']['countries']
        self.library = DirbleLibrary(backend=self)
        self.playback = DirblePlayback(audio=audio, backend=self)


class DirbleLibrary(backend.LibraryProvider):
    root_directory = Ref.directory(uri='dirble:root', name='Dirble')

    # TODO: add countries when there is a lookup for countries with stations
    def browse(self, uri):
        result = []
        variant, identifier = translator.parse_uri(uri)

        if variant == 'root':
            for category in self.backend.dirble.categories():
                result.append(translator.category_to_ref(category))
            for continent in self.backend.dirble.continents():
                result.append(translator.continent_to_ref(continent))
        elif variant == 'category' and identifier:
            for category in self.backend.dirble.subcategories(identifier):
                result.append(translator.category_to_ref(category))
            for station in self.backend.dirble.stations(category=identifier):
                result.append(translator.station_to_ref(station))
        elif variant == 'continent' and identifier:
            for country in self.backend.dirble.countries(continent=identifier):
                result.append(translator.country_to_ref(country))
        elif variant == 'country' and identifier:
            for station in self.backend.dirble.stations(country=identifier):
                result.append(
                    translator.station_to_ref(station, show_country=False))
        else:
            logger.debug('Unknown URI: %s', uri)
            return []

        result.sort(key=lambda ref: ref.name)

        # Handle this case after the general ones as we want the user defined
        # countries be the first entries, and retain their config sort order.
        if variant == 'root':
            user_countries = []
            for country_code in self.backend.countries:
                country = self.backend.dirble.country(country_code)
                if country:
                    user_countries.append(translator.country_to_ref(country))
                else:
                    logger.debug('Unknown country: %s', country_code)
            result = user_countries + result

        if not result:
            logger.debug('Did not find any browse results for: %s', uri)

        return result

    def refresh(self, uri=None):
        self.backend.dirble.flush()

    def lookup(self, uri):
        variant, identifier = translator.parse_uri(uri)
        if variant != 'station':
            return []
        station = self.backend.dirble.station(identifier)
        if not station:
            return []
        return [translator.station_to_track(station)]

    def search(self, query=None, uris=None, exact=False):
        if not query.get('any'):
            return None

        categories = set()
        countries = []

        for uri in uris or []:
            variant, identifier = translator.parse_uri(uri)
            if variant == 'country':
                countries.append(identifier.lower())
            elif variant == 'continent':
                countries.extend(self.backend.dirble.countries(identifier))
            elif variant == 'category':
                pending = [self.backend.dirble.category(identifier)]
                while pending:
                    c = pending.pop(0)
                    categories.add(c['id'])
                    pending.extend(c['children'])

        tracks = []
        for station in self.backend.dirble.search(' '.join(query['any'])):
            if countries and station['country'].lower() not in countries:
                continue
            station_categories = {c['id'] for c in station['categories']}
            if categories and not station_categories.intersection(categories):
                continue
            tracks.append(translator.station_to_track(station))

        return SearchResult(tracks=tracks)

    def get_images(self, uris):
        result = {}
        for uri in uris:
            result[uri] = []

            variant, identifier = translator.parse_uri(uri)
            if variant != 'station' or not identifier:
                continue

            station = self.backend.dirble.station(identifier)
            if not station or 'image' not in station:
                continue
            elif station['image'].get('url'):
                result[uri].append(Image(uri=station['image']['url']))
            elif station['image'].get('thumb', {}).get('url'):
                result[uri].append(Image(uri=station['image']['thumb']['url']))

        return result


class DirblePlayback(backend.PlaybackProvider):

    def translate_uri(self, uri):
        variant, identifier = translator.parse_uri(uri)
        if variant != 'station':
            return None

        station = self.backend.dirble.station(identifier)
        if not station['streams']:
            return None

        # TODO: order by bitrate and preferred mime types?
        for stream in station['streams']:
            if stream['status']:
                return stream['stream']
        return station['streams'][0]['stream']
