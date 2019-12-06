from unittest import mock

from mopidy_podcast_itunes import Extension, backend


def test_get_default_config():
    config = Extension().get_default_config()
    assert "[" + Extension.ext_name + "]" in config
    assert "enabled = true" in config


def test_get_config_schema():
    schema = Extension().get_config_schema()
    assert "base_url" in schema
    assert "country" in schema
    assert "explicit" in schema
    assert "charts" in schema
    assert "charts_limit" in schema
    assert "search_limit" in schema
    assert "timeout" in schema
    assert "retries" in schema


def test_setup():
    registry = mock.Mock()
    Extension().setup(registry)
    registry.add.assert_called_with("backend", backend.iTunesPodcastBackend)
