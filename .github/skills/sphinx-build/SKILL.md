---
name: sphinx-build
description: "Render a Sphinx project to HTML (or another builder) with sphinx-build, optionally treating warnings as errors. Use as the final generation step after scaffolding and API-stub generation to produce the documentation site."
---

# Sphinx Build

## When to use
- The last step of the Sphinx workflow, after `sphinx-scaffold` and `sphinx-apidoc`.
- With `--strict` in CI or acceptance checks to guarantee a warning-free build.

## Purpose
Invoke `sphinx-build` to turn `.rst` sources plus autodoc-imported docstrings into a
rendered site under `<docs-dir>/_build/<builder>/`.

## Parameters
| Parameter | Required | Description |
|-----------|----------|-------------|
| `--docs-dir` | yes | Sphinx source directory (must contain `conf.py`). |
| `--builder` | no | Sphinx builder name (default `html`; e.g. `dirhtml`, `latex`). |
| `--strict` | no | Add `-W --keep-going -n`; any warning fails the build. |

## Invocation
```bash
# Normal HTML build
python -m doc_agent.skills build --docs-dir docs/sphinx

# Acceptance-grade build: fail on any warning
python -m doc_agent.skills build --docs-dir docs/sphinx --strict
```

Python API: `doc_agent.skills.build(docs_dir, builder="html", strict=False) -> SkillResult`.

## Expected output
- Rendered output at `<docs-dir>/_build/<builder>/` (e.g. `index.html`, `modules.html`).
- stdout: `[build] ok: Documentation built at <abs out-dir>`.
- Exit code `0` on success; non-zero with the captured Sphinx error/warning text on
  failure (including any warning when `--strict` is set).

## Will not do
- Generate `.rst` stubs (run `sphinx-apidoc` first).
- Create `conf.py` (run `sphinx-scaffold` first).
