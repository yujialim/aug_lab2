"""Docstring analysis and insertion (workflow phases 2 and 3).

Uses the standard-library :mod:`ast` module to find modules, classes, and
functions that are missing docstrings, and inserts generated placeholder
docstrings without disturbing existing formatting or comments.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DocGap:
    """A single object that is missing a docstring."""

    kind: str  # "module", "class", or "function"
    name: str
    lineno: int  # 1-based line of the def/class statement (0 for module)


@dataclass
class FileAnalysis:
    """Result of analyzing one source file."""

    path: Path
    gaps: list[DocGap] = field(default_factory=list)
    error: str | None = None

    @property
    def has_gaps(self) -> bool:
        return bool(self.gaps)


def analyze_file(path: Path) -> FileAnalysis:
    """Parse *path* and report every object missing a docstring."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        return FileAnalysis(path=path, error=f"{type(exc).__name__}: {exc}")

    gaps: list[DocGap] = []

    if ast.get_docstring(tree) is None:
        gaps.append(DocGap(kind="module", name=path.stem, lineno=0))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node) is None:
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                gaps.append(DocGap(kind=kind, name=node.name, lineno=node.lineno))

    return FileAnalysis(path=path, gaps=gaps)


def _indent_of(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def _build_function_docstring(node: ast.FunctionDef | ast.AsyncFunctionDef, indent: str) -> list[str]:
    args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
    args += [a.arg for a in node.args.kwonlyargs]
    lines = [f'{indent}"""TODO: describe {node.name}.']
    if args:
        lines.append("")
        lines.append(f"{indent}Args:")
        for arg in args:
            lines.append(f"{indent}    {arg}: TODO.")
    if node.returns is not None:
        lines.append("")
        lines.append(f"{indent}Returns:")
        lines.append(f"{indent}    TODO.")
    lines.append(f'{indent}"""')
    return lines


def apply_docstrings(path: Path, analysis: FileAnalysis) -> int:
    """Insert generated docstrings for every gap in *analysis*.

    Returns the number of docstrings written. Insertions are applied from the
    bottom of the file upward so earlier line numbers stay valid.
    """
    if not analysis.gaps:
        return 0

    source_lines = path.read_text(encoding="utf-8").splitlines()
    tree = ast.parse("\n".join(source_lines))

    # Map lineno -> AST node for definition targets.
    nodes_by_line: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nodes_by_line[node.lineno] = node

    written = 0
    module_gap = next((g for g in analysis.gaps if g.kind == "module"), None)
    def_gaps = [g for g in analysis.gaps if g.kind != "module"]

    # Process definition docstrings bottom-up.
    for gap in sorted(def_gaps, key=lambda g: g.lineno, reverse=True):
        node = nodes_by_line.get(gap.lineno)
        if node is None or not node.body:
            continue
        first_stmt = node.body[0]
        # Skip one-line bodies like `def f(): return 1`.
        if first_stmt.lineno == node.lineno:
            continue
        insert_at = first_stmt.lineno - 1  # 0-based line index of first body stmt
        indent = _indent_of(source_lines[insert_at])
        if isinstance(node, ast.ClassDef):
            doc = [f'{indent}"""TODO: describe {node.name}."""']
        else:
            doc = _build_function_docstring(node, indent)
        source_lines[insert_at:insert_at] = doc
        written += 1

    # Module docstring goes at the top, after shebang / coding / __future__.
    if module_gap is not None:
        insert_idx = 0
        for i, line in enumerate(source_lines):
            stripped = line.strip()
            if stripped.startswith("#!") or stripped.startswith("# -*-") or "coding:" in stripped:
                insert_idx = i + 1
                continue
            if stripped.startswith("from __future__"):
                insert_idx = i + 1
                continue
            break
        module_doc = [f'"""TODO: describe the {path.stem} module."""', ""]
        source_lines[insert_idx:insert_idx] = module_doc
        written += 1

    path.write_text("\n".join(source_lines) + "\n", encoding="utf-8")
    return written
