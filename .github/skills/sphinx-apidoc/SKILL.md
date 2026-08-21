---
name: sphinx-apidoc
description: "Generate reStructuredText API stubs from a Python package using sphinx-apidoc, so autodoc has one .rst per module to render. Use after scaffolding and after docstrings are written, but before sphinx-build."
---

# Sphinx API Docs

## When to use
- After docstrings exist in the source and after `sphinx-scaffold`, to produce the
  per-module `.rst` files that `sphinx-build` renders.
- Re-run whenever the module layout changes; `--force` keeps stubs in sync.

## Purpose
Introspect a package and emit `.rst` stubs (one per module plus a `modules.rst`
table of contents) containing `automodule` directives.

## Parameters
| Parameter | Required | Description |
|-----------|----------|-------------|
| `--docs-dir` | yes | Sphinx source directory the `.rst` files are written into. |
| `--source` | yes | Package directory to introspect. |

The wrapper always passes `--force` so stale stubs are regenerated.

## Invocation
```bash
python -m doc_agent.skills apidoc --docs-dir docs/sphinx --source sample_project
```

Python API: `doc_agent.skills.apidoc(docs_dir, source_path, extra=()) -> SkillResult`.

## Expected output
- `modules.rst` and one `<package>.rst` per package under `--docs-dir`.
- stdout: `[apidoc] ok: API stubs written to <abs docs-dir>`.
- Exit code `0`; non-zero with the captured error if `sphinx-apidoc` fails or Sphinx
  is not installed.

## Will not do
- Import or execute the target code (that happens later during `sphinx-build`).
- Write docstrings — the source must already contain them (see the documentation
  pipeline's inline-docs phase).
