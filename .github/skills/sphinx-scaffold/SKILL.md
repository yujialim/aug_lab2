---
name: sphinx-scaffold
description: "Create a minimal Sphinx project (conf.py + index.rst) wired for autodoc, if one does not already exist. Use as the first Sphinx skill before generating API stubs or building, so autodoc can import the target package."
---

# Sphinx Scaffold

## When to use
- Before `sphinx-apidoc` or `sphinx-build`, when the target `docs` directory has no `conf.py` yet.
- Idempotent: safe to call every run; existing `conf.py`/`index.rst` are left untouched.

## Purpose
Generate the two files Sphinx needs to build — `conf.py` (with `autodoc`, `napoleon`,
`viewcode` enabled and the source package added to `sys.path`) and a root `index.rst`
whose toctree points at the generated `modules` stub.

## Parameters
| Parameter | Required | Description |
|-----------|----------|-------------|
| `--docs-dir` | yes | Directory that will hold the Sphinx sources and `_build/` output. |
| `--source` | yes | Package directory placed on `sys.path` so autodoc can import it. |
| `--project` | no | Human-readable project name (default `Project`). |

## Invocation
```bash
python -m doc_agent.skills scaffold --docs-dir docs/sphinx --source sample_project --project "Calculator"
```

Python API: `doc_agent.skills.scaffold(docs_dir, source_path, project) -> SkillResult`.

## Expected output
- Files `conf.py` and `index.rst` exist under `--docs-dir`.
- stdout: `[scaffold] ok: Sphinx project ready at <abs docs-dir>`.
- Exit code `0`.

## Will not do
- Overwrite an existing `conf.py` or `index.rst`.
- Run a build or generate API stubs (use `sphinx-apidoc` / `sphinx-build`).
