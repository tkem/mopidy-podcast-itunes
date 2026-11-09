# Mopidy-Podcast-iTunes

Mopidy backend extension for browsing charts and searching podcasts on Apple Podcasts
via the iTunes Search API. Pure Python ≥ 3.13, `src/` layout, no annotations; depends
on Mopidy ≥ 4, Mopidy-Podcast ≥ 4 (which plays the feeds), Pykka and `requests`.
Single maintainer; `master` is the release branch and `develop` the integration
branch that PRs and Dependabot target. Code reviews follow
`.github/copilot-instructions.md`.

## Commands

Run everything through `tox`, never bare `pytest`, `ruff` or `pyright`:

```bash
tox -p auto                                  # default environments, as CI does
tox -e py -- tests/test_browse.py -k charts  # tests; posargs go to pytest
tox -e ruff,ruff-format,docs                 # lint, format, docs
tox -e pyright                               # not in envlist yet: still fails
```

Installing Mopidy builds PyGObject, which needs the GObject introspection and cairo
headers (`libgirepository-2.0-dev`, `libcairo2-dev`, `pkg-config` on Debian/Ubuntu).
CI (GitHub Actions on `tkem/mopidy-podcast-itunes`, every push) runs CPython 3.13 and
3.14 inside the `ghcr.io/mopidy/ci` container; without `gh`, check runs via
`https://api.github.com/repos/tkem/mopidy-podcast-itunes/actions/runs?branch=<branch>`.
Coverage is reported to Codecov and is not complete; see `.github/copilot-review.md`.
`python -m mopidy_podcast_itunes.client` queries the live API for manual checks.

## Code Style

- `ruff check` and `ruff format` with the default rules; `[tool.ruff.lint]` in
  `pyproject.toml` ignores `BLE001` (errors are logged, not raised, on purpose),
  `RUF012` (Mopidy's class attributes) and `UP031`. Do not add `noqa` comments.
- No type annotations in `src/`; keep the code compatible with pyright's
  `standard` mode where it is cheap to do so.
- Private state uses double-underscore names (`self.__session`); all HTTP goes
  through `iTunesPodcastClient`, which returns decoded JSON, never `requests` objects.
- Log with `logger.error("... %s", arg)`, never f-strings; skip and log single bad
  results instead of failing a whole `browse()` or `search()`.
- Docs (`docs/index.rst`): wrap prose at column 70, two spaces after a sentence,
  `confval` entries for every setting in `ext.conf`. Keep `README.rst` in sync.

## Architecture Constraints

- Browse URIs are `podcast+itunes:` (root, genre 26 "Podcasts"),
  `podcast+itunes:genre:<id>` and `podcast+itunes:charts:<id>`. Results point at
  Mopidy-Podcast URIs, `podcast+<feed URL>` and `podcast+<feed URL>#<guid>`, built by
  `translator.uri()` with the same encoding as Mopidy-Podcast; keep them identical.
- Charts come from the RSS `toppodcasts` JSON, which lacks feed URLs, so the client
  resolves the entry IDs with one `/lookup` call. Genres are fetched once per root id
  and cached in the client until `refresh()`.
- `translator.query()` raises `NotImplementedError` for unsupported queries (exact,
  multi-key, unknown field); `search()` then returns `None` so Mopidy asks other
  backends. Only the fields in `_QUERY` map to iTunes `entity`/`attribute`.
- `translator.model()` raises `TypeError` and `translator.ref()` `ValueError` for
  unsupported result kinds, `KeyError` for incomplete items; callers log and skip.
- Configuration keys live in `ext.conf` and `Extension.get_config_schema()`; both
  must change together, as must the test `config` fixture. `MAX_LIMIT` is the API's.

## Testing

- New behavior needs tests under `tests/`; user-visible changes need docs in
  `docs/index.rst`. Tests never touch the network: mock HTTP with `responses`
  (`@responses.activate` and URL regexes) and use minimal JSON fixtures.
- Provider tests build a real `iTunesPodcastBackend` from the `config` fixture with a
  mock `audio`; translator tests are parametrized over raw API items.

## Boundaries

- Never edit `CHANGELOG.rst` or bump `__version__`; both are release-only.
- Never change URIs or configuration keys without a deprecation path.
- Do not re-raise the *Maintainer Decisions* in `.github/copilot-instructions.md`.

## Git

- PRs target `develop` and reference an open issue (except trivial fixes), in
  separate commits:
  `Fix #123: ...`, `Tests for #123: ...`, `Docs for #123: ...`.
- Run `tox -p auto` before pushing. Update this file in the same PR that changes a
  convention, and keep it under 100 lines.
