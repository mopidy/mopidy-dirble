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
        user_countries = []
        categories = []
        geographic = []
        tracks = []
        limit = 20
        next_offset = None

        variant, identifier, offset = translator.parse_uri(uri)

        if variant == 'root':
            for category in self.backend.dirble.categories():
                categories.append(translator.category_to_ref(category))
            for continent in self.backend.dirble.continents():
                geographic.append(translator.continent_to_ref(continent))
        elif variant == 'category' and identifier:
            if not offset:
                for category in self.backend.dirble.subcategories(identifier):
                    categories.append(translator.category_to_ref(category))
            stations, next_offset = self.backend.dirble.stations(
                category=identifier, offset=offset or 0, limit=limit)
            for station in stations:
                tracks.append(translator.station_to_ref(station))
        elif variant == 'continent' and identifier:
            for country in self.backend.dirble.countries(continent=identifier):
                geographic.append(translator.country_to_ref(country))
        elif variant == 'country' and identifier:
            stations, next_offset = self.backend.dirble.stations(
                country=identifier, offset=offset or 0, limit=limit)
            for station in stations:
                tracks.append(
                    translator.station_to_ref(station, show_country=False))
        else:
            logger.debug('Unknown URI: %s', uri)
            return []

        if variant == 'root':
            for country_code in self.backend.countries:
                country = self.backend.dirble.country(country_code)
                if country:
                    user_countries.append(translator.country_to_ref(country))
                else:
                    logger.debug('Unknown country: %s', country_code)

        categories.sort(key=lambda ref: ref.name)
        geographic.sort(key=lambda ref: ref.name)

        result = user_countries + geographic + categories + tracks

        if not result:
            logger.debug('Did not find any browse results for: %s', uri)

        if next_offset:
            next_uri = translator.unparse_uri(variant, identifier, next_offset)
            result.append(Ref.directory(uri=next_uri, name='Next page'))

        return result

    def refresh(self, uri=None):
        self.backend.dirble.flush()

    def lookup(self, uri):
        variant, identifier, _ = translator.parse_uri(uri)
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

        # TODO: Redo this bit now that dirble can filter by country/category.
        for uri in uris or []:
            variant, identifier, _ = translator.parse_uri(uri)
            if variant == 'country':
                countries.append(identifier.lower())
            elif variant == 'continent':
                # TODO: This probably fails as we expect lower country code,
                # not a full country object.
                countries.extend(self.backend.dirble.countries(identifier))
            elif variant == 'category':
                pending = [self.backend.dirble.category(identifier)]
                while pending:
                    c = pending.pop(0)
                    categories.add(c['id'])
                    pending.extend(c['children'])

        tracks = []
        stations, _ = self.backend.dirble.search(
            ' '.join(query['any']), limit=20)
        for station in stations:
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

            variant, identifier, _ = translator.parse_uri(uri)
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
        variant, identifier, _ = translator.parse_uri(uri)
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
