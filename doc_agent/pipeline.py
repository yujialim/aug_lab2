"""State-machine pipeline that drives the documentation workflow.

Each workflow phase is a state. The pipeline advances through the states in
order, records a :class:`PhaseResult` for each, and stops early on a fatal
error. Every phase is wrapped in error handling and structured logging so a
failure in one phase is captured rather than crashing the run.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

from . import docstrings, sphinx_build

logger = logging.getLogger("doc_agent")


class Phase(str, Enum):
    """The five documentation workflow phases, in execution order."""

    SCOPE = "scope_identification"
    ANALYSIS = "file_logic_analysis"
    INLINE_DOCS = "inline_documentation"
    SPHINX = "sphinx_generation"
    REVIEW = "review_maintenance"


@dataclass
class PhaseResult:
    """Outcome of a single phase."""

    phase: Phase
    status: str  # "ok", "warning", or "failed"
    summary: str
    data: dict = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Aggregate outcome of a full pipeline run."""

    phases: list[PhaseResult] = field(default_factory=list)
    docstrings_written: int = 0
    docs_built: bool = False

    @property
    def ok(self) -> bool:
        return all(p.status != "failed" for p in self.phases)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "docstrings_written": self.docstrings_written,
            "docs_built": self.docs_built,
            "phases": [
                {**asdict(p), "phase": p.phase.value} for p in self.phases
            ],
        }


class DocumentationPipeline:
    """Execute the documentation workflow over a target codebase."""

    def __init__(
        self,
        source_path: Path,
        docs_dir: Path,
        project: str = "Sample Project",
        run_sphinx: bool = True,
        exclude: tuple[str, ...] = ("_build", "tests", ".venv", "__pycache__"),
    ) -> None:
        self.source_path = Path(source_path)
        self.docs_dir = Path(docs_dir)
        self.project = project
        self.run_sphinx = run_sphinx
        self.exclude = exclude
        self.result = PipelineResult()
        self._files: list[Path] = []
        self._analyses: list[docstrings.FileAnalysis] = []

    # -- state machine driver ------------------------------------------------

    def run(self) -> PipelineResult:
        """Run every phase in order, stopping on a fatal error."""
        transitions = {
            Phase.SCOPE: self._phase_scope,
            Phase.ANALYSIS: self._phase_analysis,
            Phase.INLINE_DOCS: self._phase_inline_docs,
            Phase.SPHINX: self._phase_sphinx,
            Phase.REVIEW: self._phase_review,
        }
        for phase, handler in transitions.items():
            logger.info("=> entering phase: %s", phase.value)
            try:
                outcome = handler()
            except Exception as exc:  # defensive: never crash the whole run
                logger.exception("phase %s raised an unexpected error", phase.value)
                outcome = PhaseResult(
                    phase=phase,
                    status="failed",
                    summary=f"Unhandled error: {type(exc).__name__}: {exc}",
                )
            self.result.phases.append(outcome)
            logger.info("<= phase %s: %s — %s", phase.value, outcome.status, outcome.summary)
            if outcome.status == "failed":
                logger.error("stopping pipeline: phase %s failed", phase.value)
                break
        self._write_run_summary()
        return self.result

    # -- phase 1: scope identification --------------------------------------

    def _phase_scope(self) -> PhaseResult:
        if not self.source_path.exists():
            return PhaseResult(
                phase=Phase.SCOPE,
                status="failed",
                summary=f"Source path does not exist: {self.source_path}",
            )
        self._files = [
            p
            for p in self.source_path.rglob("*.py")
            if not any(part in self.exclude for part in p.parts)
        ]
        if not self._files:
            return PhaseResult(
                phase=Phase.SCOPE,
                status="failed",
                summary=f"No Python files found under {self.source_path}",
            )
        return PhaseResult(
            phase=Phase.SCOPE,
            status="ok",
            summary=f"Identified {len(self._files)} source file(s) in scope.",
            data={"files": [str(p) for p in self._files]},
        )

    # -- phase 2: file / logic analysis -------------------------------------

    def _phase_analysis(self) -> PhaseResult:
        self._analyses = [docstrings.analyze_file(p) for p in self._files]
        errors = [a for a in self._analyses if a.error]
        total_gaps = sum(len(a.gaps) for a in self._analyses)
        status = "warning" if errors else "ok"
        for a in errors:
            logger.warning("could not analyze %s: %s", a.path, a.error)
        return PhaseResult(
            phase=Phase.ANALYSIS,
            status=status,
            summary=f"Found {total_gaps} missing docstring(s); {len(errors)} file(s) unparseable.",
            data={"total_gaps": total_gaps, "unparseable": [str(a.path) for a in errors]},
        )

    # -- phase 3: inline documentation application --------------------------

    def _phase_inline_docs(self) -> PhaseResult:
        written = 0
        for analysis in self._analyses:
            if analysis.error or not analysis.has_gaps:
                continue
            try:
                written += docstrings.apply_docstrings(analysis.path, analysis)
            except Exception as exc:
                logger.exception("failed to write docstrings into %s", analysis.path)
                return PhaseResult(
                    phase=Phase.INLINE_DOCS,
                    status="failed",
                    summary=f"Docstring insertion failed for {analysis.path}: {exc}",
                )
        self.result.docstrings_written = written
        return PhaseResult(
            phase=Phase.INLINE_DOCS,
            status="ok",
            summary=f"Wrote {written} docstring(s) before Sphinx generation.",
            data={"docstrings_written": written},
        )

    # -- phase 4: sphinx automation and generation --------------------------

    def _phase_sphinx(self) -> PhaseResult:
        if not self.run_sphinx:
            return PhaseResult(
                phase=Phase.SPHINX,
                status="warning",
                summary="Sphinx generation skipped (run_sphinx=False).",
            )
        outcome = sphinx_build.generate(self.docs_dir, self.source_path, self.project)
        self.result.docs_built = outcome.build_ok
        if outcome.build_ok:
            status = "ok"
        elif not sphinx_build.sphinx_available():
            status = "warning"  # missing tooling is not a pipeline failure
        else:
            status = "failed"
        return PhaseResult(
            phase=Phase.SPHINX,
            status=status,
            summary=outcome.message,
            data={"apidoc_ok": outcome.apidoc_ok, "build_ok": outcome.build_ok},
        )

    # -- phase 5: review and maintenance ------------------------------------

    def _phase_review(self) -> PhaseResult:
        remaining = 0
        for path in self._files:
            remaining += len(docstrings.analyze_file(path).gaps)
        status = "ok" if remaining == 0 else "warning"
        summary = (
            "All targeted objects are documented."
            if remaining == 0
            else f"{remaining} object(s) still lack docstrings; re-run to re-enter scope."
        )
        return PhaseResult(
            phase=Phase.REVIEW,
            status=status,
            summary=summary,
            data={"remaining_gaps": remaining},
        )

    # -- helpers -------------------------------------------------------------

    def _write_run_summary(self) -> None:
        summary_path = self.docs_dir / "pipeline_run.json"
        try:
            self.docs_dir.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(
                json.dumps(self.result.to_dict(), indent=2), encoding="utf-8"
            )
            logger.info("run summary written to %s", summary_path)
        except OSError as exc:
            logger.warning("could not write run summary: %s", exc)
