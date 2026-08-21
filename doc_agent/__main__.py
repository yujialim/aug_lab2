"""Command-line entry point for the Documentation Agent pipeline.

Example:
    python -m doc_agent --path sample_project --docs-dir docs/sphinx --project "Calculator"
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .pipeline import DocumentationPipeline


def _configure_logging(docs_dir: Path, verbose: bool) -> None:
    docs_dir.mkdir(parents=True, exist_ok=True)
    log_path = docs_dir / "doc_agent_run.log"
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, mode="w", encoding="utf-8"),
    ]
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        handlers=handlers,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the documentation workflow pipeline.")
    parser.add_argument("--path", required=True, help="Source code directory to document.")
    parser.add_argument("--docs-dir", default="docs/sphinx", help="Sphinx output directory.")
    parser.add_argument("--project", default="Sample Project", help="Project name for Sphinx.")
    parser.add_argument("--no-sphinx", action="store_true", help="Skip the Sphinx build phase.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args(argv)

    docs_dir = Path(args.docs_dir)
    _configure_logging(docs_dir, args.verbose)

    pipeline = DocumentationPipeline(
        source_path=Path(args.path),
        docs_dir=docs_dir,
        project=args.project,
        run_sphinx=not args.no_sphinx,
    )
    result = pipeline.run()

    logging.getLogger("doc_agent").info(
        "run complete: ok=%s docstrings_written=%d docs_built=%s",
        result.ok,
        result.docstrings_written,
        result.docs_built,
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
