from __future__ import unicode_literals

import unittest

from mopidy_podcast_itunes import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()
        config = ext.get_default_config()
        self.assertIn('[podcast-itunes]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = Extension()
        schema = ext.get_config_schema()
        self.assertIn('base_url', schema)
        self.assertIn('root_name', schema)
        self.assertIn('genre_format', schema)
        self.assertIn('podcast_format', schema)
        self.assertIn('episode_format', schema)
        self.assertIn('charts', schema)
        self.assertIn('charts_format', schema)
        self.assertIn('country', schema)
        self.assertIn('explicit', schema)
        self.assertIn('timeout', schema)
