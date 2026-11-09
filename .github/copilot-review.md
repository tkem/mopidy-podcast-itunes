# Code Review — Mopidy-Podcast-iTunes 4.0.0

**Date:** 2026-11-09
**Reviewed:** `develop` at `46fa4ac` ("Fix HTTP, timeout and connection errors
propagating from search(). (#3)"), i.e. v4.0.0 plus the build environment update
and the two `search()` fixes.

**CI status:** All default `tox` environments pass locally on CPython 3.13.18 (`py`:
30 passed) with Mopidy 4.0.5, Mopidy-Podcast 4.0.0 and requests 2.34.2; not run on
3.14 locally. GitHub Actions passed on 3.13 and 3.14 for the merged PRs; its run
for this commit had not finished when this review was written. `tox -e pyright`
fails with 38 errors (Code #3). **Coverage:** 93 % with branches; gaps in
`library.py` (90 %: invalid URIs, `refresh()`, skipped chart items) and the
`translator.query()` errors.

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `library.py` `browse` | A URI with fewer or more than three `:`-separated parts (e.g. `podcast+itunes:charts`) raises `ValueError`; an unknown type logs "Invalid browse URI" and returns `None` instead of `[]`. Errors from `client.charts()`/`genre()` (HTTP, unknown genre id: `KeyError`) also propagate. |
| 2 | Low | `translator.py` `_MODELS` / `_REFS` | `item.get("collectionName", item["trackName"])` evaluates the default eagerly, so a podcast item with `collectionName` but no `trackName` is skipped with `KeyError`. |
| 3 | Low | whole package, `tests/` | pyright `standard` reports 38 errors: Mopidy 4's typed models (`Uri`, `ReleaseDate`, `DurationMs`, `frozenset` artists, `tuple` search results) reject plain `str`, `int` and `list` arguments, `self.backend.client` is unknown on `backend.Backend`, and `browse()` overrides `LibraryProvider.browse()` incompatibly. Blocks adding `pyright` to the envlist. |

## Tests — Gaps

| # | Priority | Finding |
|---|----------|---------|
| 1 | Low | HTTP errors and timeouts are tested for the search API only; none covers `charts()` or `genre()` (Code #1). |
| 2 | Low | `browse()` with an invalid URI, `refresh()` and the charts path that skips items with missing keys (lines 74–79) are untested. |
| 3 | Info | `translator.query()` is tested only for supported queries; the three `NotImplementedError` branches and `search()` returning `None` for them are not. |
| 4 | Info | The `config` fixture still carries the removed `charts` key; two `DeprecationWarning`s come from `mopidy.types` at import time, not from this package. |

## Changelog

| # | Priority | Finding |
|---|----------|---------|
| 1 | Medium | The next release's entry needs "Fix ``UnboundLocalError`` in ``search()`` if the query cannot be translated." and "Fix HTTP, timeout and connection errors propagating from ``search()``.", plus "Update build environment." for the ruff, `tox` and CI changes and the removal of `setup.cfg` and `setup.py`. |
