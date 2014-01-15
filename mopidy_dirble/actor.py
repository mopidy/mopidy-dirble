from __future__ import unicode_literals

import json
import logging
import urllib

import pykka

from mopidy import backend

logger = logging.getLogger(__name__)


class DirbleBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = ['dirble']

    def __init__(self, config, audio):
        super(DirbleBackend, self).__init__()
        self.library = DirbleLibrary(backend=self, config=config)


class DirbleLibrary(backend.LibraryProvider):
    root_directory_name = 'dirble'

    def __init__(self, backend, config):
        super(DirbleLibrary, self).__init__(backend)

    def browse(self, path):
        return []

    def refresh(self, uri=None):
        pass

    def lookup(self, uri):
        return []

    def find_exact(self, query=None, uris=None):
        return None

    def search(self, query=None, uris=None):
        return None
