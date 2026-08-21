"""Documentation Agent automation package.

Implements the five-phase documentation workflow as an executable pipeline:

1. Scope identification
2. File / logic analysis
3. Inline documentation application
4. Sphinx automation and generation
5. Review and maintenance
"""

from .pipeline import DocumentationPipeline, Phase, PipelineResult

__all__ = ["DocumentationPipeline", "Phase", "PipelineResult"]
