# Documentation Workflow

End-to-end workflow for producing and maintaining engineering documentation, from
scope identification through Sphinx generation and ongoing maintenance. The diagram
highlights every point where the **Documentation Agent** interacts with the process.

## Workflow diagram

```mermaid
flowchart TD
    Start([Trigger: docs out of sync / new module]) --> P1

    subgraph P1 [Phase 1 · Scope Identification]
        A1[Identify documentation scope:<br/>one file, one module, or one doc class]
        A2[List target artifacts:<br/>API refs, ADRs, READMEs, runbooks]
        A1 --> A2
    end

    subgraph P2 [Phase 2 · File / Logic Analysis]
        B1[Load code with<br/>source-code-context skill]
        B2[Map each documented claim to code]
        B3{Claim status?}
        B1 --> B2 --> B3
    end

    subgraph P3 [Phase 3 · Inline Documentation Application]
        C1[Apply smallest edits:<br/>docstrings, comments, type hints]
        C2[Preserve existing tone & structure]
        C1 --> C2
    end

    subgraph P4 [Phase 4 · Sphinx Automation & Generation]
        D1[sphinx-apidoc:<br/>generate .rst stubs from source]
        D2[sphinx-build:<br/>autodoc pulls docstrings into HTML/PDF]
        D3[Publish rendered output]
        D1 --> D2 --> D3
    end

    subgraph P5 [Phase 5 · Review & Maintenance]
        E1[Reviewer checklist]
        E2[Stale-sections & disagreement report]
        E3{Docs accurate?}
        E1 --> E2 --> E3
    end

    P1 --> P2
    B3 -- matches --> P4
    B3 -- stale / contradicts --> P3
    B3 -- unverifiable --> E2
    P3 --> P4
    P4 --> P5
    E3 -- yes --> Done([Published & in sync])
    E3 -- no, drift found --> P1

    %% Documentation Agent interaction points
    DA{{Documentation Agent}}
    DA -. drives .-> A1
    DA -. drives .-> B2
    DA -. drives .-> C1
    DA -. validates .-> D2
    DA -. authors .-> E2

    classDef agent fill:#2b6cb0,stroke:#1a365d,color:#ffffff,stroke-width:2px;
    classDef phase fill:#f7fafc,stroke:#4a5568,color:#1a202c;
    class DA agent;
```

> The blue **Documentation Agent** node uses dotted edges to mark each phase it acts on.
> It authors and edits documentation only — it never changes source code, tests, or
> configuration (code/doc disagreements are reported, not "fixed").

## Phase notes

| # | Phase | Purpose | Documentation Agent role | Key dependency |
|---|-------|---------|--------------------------|----------------|
| 1 | Scope Identification | Bound the work to one file, module, or document class and enumerate target artifacts. | Selects scope and target artifacts. | A trigger (drift, new/changed code). |
| 2 | File / Logic Analysis | Load the relevant code and map every documented claim to its source; classify as matches / stale / contradicts / unverifiable. | Runs analysis via the `source-code-context` skill and categorizes claims. | Scope from Phase 1. |
| 3 | Inline Documentation Application | Apply the smallest edits — docstrings, comments, type hints — while preserving tone and structure. | Authors the inline documentation edits. | Stale/contradicting claims from Phase 2. |
| 4 | Sphinx Automation & Generation | `sphinx-apidoc` scaffolds `.rst`; `sphinx-build` + autodoc render docstrings into HTML/PDF; publish. | Validates that autodoc output reflects the edits. | Inline docs from Phase 3 (or already-matching claims). |
| 5 | Review & Maintenance | Reviewer checklist, stale-sections report, and drift detection that loops back to Phase 1. | Authors the reviewer checklist and stale-sections report. | Generated docs from Phase 4. |

## Sequence & dependency summary

- **Linear spine:** Phase 1 → 2 → 3 → 4 → 5, then a maintenance loop back to Phase 1 when drift is detected.
- **Branch in Phase 2:** claims that already *match* skip inline editing and go straight to Sphinx generation; *stale/contradicting* claims route to Phase 3; *unverifiable* claims are logged in the Phase 5 report rather than restated.
- **Feedback loop:** if review finds the docs inaccurate, the workflow re-enters at scope identification.

## Rendering to PNG / PDF

The Mermaid block above is the editable source. To export a static image:

```bash
# PNG
npx @mermaid-js/mermaid-cli -i docs/documentation-workflow.md -o docs/documentation-workflow.png

# PDF
npx @mermaid-js/mermaid-cli -i docs/documentation-workflow.md -o docs/documentation-workflow.pdf
```

In VS Code, the Markdown preview renders the diagram directly, and the Mermaid
extension offers a right-click **Export** to PNG/SVG.
