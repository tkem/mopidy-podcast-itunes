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
        self.assertIn('display_name', schema)
        self.assertIn('base_url', schema)
        self.assertIn('country', schema)
        self.assertIn('browse_charts', schema)
        self.assertIn('browse_limit', schema)
        self.assertIn('root_genre_id', schema)
        self.assertIn('explicit', schema)
        self.assertIn('timeout', schema)
