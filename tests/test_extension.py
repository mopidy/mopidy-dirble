from __future__ import unicode_literals

import unittest

from mopidy_dirble import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[dirble]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()
        self.assertIn('api_key', schema)

    # TODO Write more tests
