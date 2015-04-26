from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Image, Ref

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
            for country in self.backend.countries:
                result.append(translator.country_to_ref(country))
            for continent in self.backend.dirble.continents():
                result.append(translator.continent_to_ref(continent))
        elif variant == 'category' and identifier:
            for category in self.backend.dirble.categories(identifier):
                result.append(translator.category_to_ref(category))
            for station in self.backend.dirble.stations(category=identifier):
                result.append(translator.station_to_ref(station))
        elif variant == 'continent' and identifier:
            for country in self.backend.dirble.countries(identifier):
                result.append(translator.country_to_ref(country))
        elif variant == 'country' and identifier:
            for station in self.backend.dirble.stations(country=identifier):
                result.append(translator.station_to_ref(station, False))
        else:
            logger.debug('Unknown URI: %s', uri)

        result.sort(key=lambda ref: ref.name)
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

    def get_images(self, uris):
        result = {}
        for uri in uris:
            result[uri] = []

            variant, identifier = translator.parse_uri(uri)
            if variant != 'station' or not identifier:
                continue

            station = self.backend.dirble.station(identifier)
            if not station:
                continue

            if station['image']['image']['url']:
                result[uri].append(Image(uri=station['image']['image']['url']))

        return result


class DirblePlayback(backend.PlaybackProvider):

    def translate_uri(self, uri):
        variant, identifier = translator.parse_uri(uri)
        if variant != 'station':
            return None
        station = self.backend.dirble.station(identifier)
        for stream in station['streams']:
            # TODO: add way to pick which variant to use?
            return stream['stream']
        return None
