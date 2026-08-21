---
name: sphinx-clean
description: "Remove the Sphinx _build output directory so the next build starts fresh. Use before a strict or release build, or when stale cached output is causing spurious warnings."
---

# Sphinx Clean

## When to use
- Before a `--strict` build, to avoid warnings from stale cached pages.
- To reclaim space or reset the docs output between runs.

## Purpose
Delete `<docs-dir>/_build/`. Generated `.rst` stubs and `conf.py` are left in place;
only rendered output and Sphinx's doctree cache are removed.

## Parameters
| Parameter | Required | Description |
|-----------|----------|-------------|
| `--docs-dir` | yes | Sphinx source directory whose `_build/` should be removed. |

## Invocation
```bash
python -m doc_agent.skills clean --docs-dir docs/sphinx
```

Python API: `doc_agent.skills.clean(docs_dir) -> SkillResult`.

## Expected output
- `<docs-dir>/_build/` no longer exists.
- stdout: `[clean] ok: Removed <abs build-dir>` (or `Nothing to clean.`).
- Exit code `0` (a missing build directory is not an error).

## Will not do
- Delete `conf.py`, `index.rst`, or generated `.rst` stubs.
- Touch anything outside `<docs-dir>/_build/`.
