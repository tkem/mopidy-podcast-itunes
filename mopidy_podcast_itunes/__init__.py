from __future__ import unicode_literals

from mopidy import config, ext

__version__ = '0.0.1'

BOOL_CHOICES = ('Yes', 'No')


class Extension(ext.Extension):

    dist_name = 'Mopidy-Podcast-iTunes'
    ext_name = 'podcast-itunes'
    version = __version__

    def get_default_config(self):
        import os
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['base_url'] = config.String()
        schema['label'] = config.String()
        schema['country'] = config.String()
        schema['search_limit'] = config.Integer(minimum=1, maximum=200)
        schema['root_genre_id'] = config.String()
        schema['charts_name'] = config.String()
        schema['charts_limit'] = config.Integer(minimum=1, maximum=200)
        schema['explicit'] = config.String(optional=True, choices=BOOL_CHOICES)
        schema['timeout'] = config.Integer(optional=True)
        return schema

    def setup(self, registry):
        from .directory import iTunesDirectory
        registry.add('podcast:directory', iTunesDirectory)
