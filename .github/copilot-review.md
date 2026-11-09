# Code Review — Mopidy-Podcast-iTunes 4.0.0

**Date:** 2026-11-09
**Reviewed:** branch `build-environment` (two commits: "Update build environment and
add AGENTS.md." and "Configure ruff and pyright, apply ruff fixes."), based on
`develop` at `5faf680` ("Bump codecov/codecov-action from 7.0.0 to 7.1.1"), i.e.
v4.0.0 plus dependency bumps.

**CI status:** All default `tox` environments pass locally on CPython 3.13.18 (`py`:
26 passed) with Mopidy 4.0.5, Mopidy-Podcast 4.0.0 and requests 2.34.2; not run on
3.14. `tox -e pyright` fails with 39 errors (Code #5). GitHub Actions has not run
for this branch. **Coverage:** 90 % with branches; gaps in `library.py` (86 %:
invalid URIs, `refresh()`, search errors) and the `translator.query()` errors.

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Medium | `library.py` `search` | If `translator.query()` raises anything but `NotImplementedError`, the error is logged and the loop then uses the unbound `kwargs`, raising `UnboundLocalError` out of `search()`. Suggested fix: `return None` in that `except` clause. |
| 2 | Medium | `client.py` `iTunesPodcastClient.search` | Catches `urllib.error.HTTPError`, but `response.raise_for_status()` raises `requests.HTTPError`, so an HTTP 503 from the search API propagates out of `library.search()` instead of returning no results. Same for timeouts and connection errors. |
| 3 | Low | `library.py` `browse` | A URI with fewer or more than three `:`-separated parts (e.g. `podcast+itunes:charts`) raises `ValueError`; an unknown type logs "Invalid browse URI" and returns `None` instead of `[]`. Errors from `client.charts()`/`genre()` (HTTP, unknown genre id: `KeyError`) also propagate. |
| 4 | Low | `translator.py` `_MODELS` / `_REFS` | `item.get("collectionName", item["trackName"])` evaluates the default eagerly, so a podcast item with `collectionName` but no `trackName` is skipped with `KeyError`. |
| 5 | Low | whole package, `tests/` | pyright `standard` reports 39 errors: Mopidy 4's typed models (`Uri`, `ReleaseDate`, `DurationMs`, `frozenset` artists, `tuple` search results) reject plain `str`, `int` and `list` arguments, `self.backend.client` is unknown on `backend.Backend`, plus Code #1. Blocks adding `pyright` to the envlist. |

## Tests — Gaps

| # | Priority | Finding |
|---|----------|---------|
| 1 | Low | No test covers HTTP errors or timeouts from any endpoint, so Code #2 went unnoticed; `responses` can return status codes and raise `ConnectionError` directly. |
| 2 | Low | `browse()` with an invalid URI, `refresh()` and the charts path that skips items with missing keys (lines 73–78) are untested. |
| 3 | Info | `translator.query()` is tested only for supported queries; the three `NotImplementedError` branches and `search()` returning `None` for them are not. |
| 4 | Info | The `config` fixture still carries the removed `charts` key; two `DeprecationWarning`s come from `mopidy.types` at import time, not from this package. |

## Docs (`docs/index.rst`)

| # | Priority | Finding |
|---|----------|---------|
| 1 | Info | `README.rst` still shows a "code style: black" badge, although formatting is done with `ruff format`. |

## Changelog

| # | Priority | Finding |
|---|----------|---------|
| 1 | Info | The build changes on this branch (ruff configuration, `tox` and CI updates, removal of `setup.cfg` and `setup.py`) need an "Update build environment." line in the next release's entry. |
