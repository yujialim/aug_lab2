"""Reusable Sphinx skills the agent can invoke individually.

Each skill is a thin, deterministic wrapper around a Sphinx command. They are
callable both as Python functions and from the command line:

    python -m doc_agent.skills scaffold --docs-dir docs/sphinx --source sample_project --project "Calculator"
    python -m doc_agent.skills apidoc   --docs-dir docs/sphinx --source sample_project
    python -m doc_agent.skills build    --docs-dir docs/sphinx --strict
    python -m doc_agent.skills clean    --docs-dir docs/sphinx

Every skill returns a :class:`SkillResult` and, from the CLI, exits non-zero on
failure so an agent or CI step can branch on the outcome.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .sphinx_build import ensure_project, sphinx_available


@dataclass
class SkillResult:
    """Outcome of a single skill invocation."""

    ok: bool
    message: str
    returncode: int = 0


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def scaffold(docs_dir: Path, source_path: Path, project: str) -> SkillResult:
    """Create a minimal Sphinx project (conf.py + index.rst) if absent.

    Parameters:
        docs_dir: Directory that will hold the Sphinx sources and build output.
        source_path: Package directory to put on ``sys.path`` for autodoc.
        project: Human-readable project name.

    Returns:
        SkillResult describing whether the scaffold now exists.
    """
    abs_docs = docs_dir.resolve()
    ensure_project(abs_docs, source_path.resolve(), project)
    return SkillResult(ok=True, message=f"Sphinx project ready at {abs_docs}")


def apidoc(docs_dir: Path, source_path: Path, extra: tuple[str, ...] = ()) -> SkillResult:
    """Generate ``.rst`` API stubs from source with ``sphinx-apidoc``.

    Parameters:
        docs_dir: Sphinx source directory to write ``.rst`` files into.
        source_path: Package directory to introspect.
        extra: Additional ``sphinx-apidoc`` flags (``--force`` is always added).

    Returns:
        SkillResult; ``ok`` is False if apidoc exits non-zero.
    """
    if not sphinx_available():
        return SkillResult(ok=False, message="Sphinx is not installed.", returncode=1)
    abs_docs = docs_dir.resolve()
    proc = _run(
        [sys.executable, "-m", "sphinx.ext.apidoc", "-o", str(abs_docs),
         str(source_path.resolve()), "--force", *extra],
        cwd=abs_docs,
    )
    if proc.returncode != 0:
        return SkillResult(ok=False, message=proc.stderr.strip(), returncode=proc.returncode)
    return SkillResult(ok=True, message=f"API stubs written to {abs_docs}")


def build(docs_dir: Path, builder: str = "html", strict: bool = False) -> SkillResult:
    """Run ``sphinx-build`` to render the documentation.

    Parameters:
        docs_dir: Sphinx source directory (must contain ``conf.py``).
        builder: Sphinx builder name, e.g. ``html`` or ``dirhtml``.
        strict: When True, add ``-W --keep-going -n`` so warnings fail the build.

    Returns:
        SkillResult; ``ok`` is False if the build reports errors (or warnings
        when ``strict`` is set).
    """
    if not sphinx_available():
        return SkillResult(ok=False, message="Sphinx is not installed.", returncode=1)
    abs_docs = docs_dir.resolve()
    out_dir = abs_docs / "_build" / builder
    flags = ["-W", "--keep-going", "-n"] if strict else []
    proc = _run(
        [sys.executable, "-m", "sphinx", "-b", builder, *flags, str(abs_docs), str(out_dir)],
        cwd=abs_docs,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return SkillResult(ok=False, message=detail, returncode=proc.returncode)
    return SkillResult(ok=True, message=f"Documentation built at {out_dir}")


def clean(docs_dir: Path) -> SkillResult:
    """Delete the Sphinx ``_build`` output directory.

    Parameters:
        docs_dir: Sphinx source directory whose build output should be removed.

    Returns:
        SkillResult; always ``ok`` (a missing build directory is not an error).
    """
    build_root = docs_dir.resolve() / "_build"
    if build_root.exists():
        shutil.rmtree(build_root)
        return SkillResult(ok=True, message=f"Removed {build_root}")
    return SkillResult(ok=True, message="Nothing to clean.")


# -- command line -----------------------------------------------------------


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reusable Sphinx skills.")
    sub = parser.add_subparsers(dest="skill", required=True)

    p_scaffold = sub.add_parser("scaffold", help="Create conf.py + index.rst.")
    p_scaffold.add_argument("--docs-dir", required=True)
    p_scaffold.add_argument("--source", required=True)
    p_scaffold.add_argument("--project", default="Project")

    p_apidoc = sub.add_parser("apidoc", help="Generate .rst API stubs.")
    p_apidoc.add_argument("--docs-dir", required=True)
    p_apidoc.add_argument("--source", required=True)

    p_build = sub.add_parser("build", help="Render the documentation.")
    p_build.add_argument("--docs-dir", required=True)
    p_build.add_argument("--builder", default="html")
    p_build.add_argument("--strict", action="store_true")

    p_clean = sub.add_parser("clean", help="Remove the _build directory.")
    p_clean.add_argument("--docs-dir", required=True)

    args = parser.parse_args(argv)

    if args.skill == "scaffold":
        result = scaffold(Path(args.docs_dir), Path(args.source), args.project)
    elif args.skill == "apidoc":
        result = apidoc(Path(args.docs_dir), Path(args.source))
    elif args.skill == "build":
        result = build(Path(args.docs_dir), args.builder, args.strict)
    elif args.skill == "clean":
        result = clean(Path(args.docs_dir))
    else:  # pragma: no cover - argparse enforces choices
        parser.error(f"unknown skill: {args.skill}")

    print(f"[{args.skill}] {'ok' if result.ok else 'FAILED'}: {result.message}")
    return 0 if result.ok else (result.returncode or 1)


if __name__ == "__main__":
    raise SystemExit(_main())
