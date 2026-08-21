# Documentation Workflow

A clear, end-to-end view of the documentation process, from identifying what needs to be
documented through generating output with Sphinx and keeping it maintained. The diagram
shows the five workflow phases, their sequence and dependencies, and the points where the
documentation agent interacts with the workflow.

## Workflow diagram

```mermaid
flowchart TD
    Start([Start: documentation needed]) --> P1

    subgraph P1 [Phase 1 · Scope Identification]
        A1[Determine what needs documenting:<br/>module, package, or public API]
        A2[Define audience & documentation goals]
        A1 --> A2
    end

    subgraph P2 [Phase 2 · File / Logic Analysis]
        B1[Read source files in scope]
        B2[Understand functions, classes,<br/>parameters, and return values]
        B3[Identify gaps and undocumented logic]
        B1 --> B2 --> B3
    end

    subgraph P3 [Phase 3 · Inline Documentation Application]
        C1[Write docstrings for<br/>modules, classes, functions]
        C2[Add inline comments for complex logic]
        C3[Follow a consistent docstring style]
        C1 --> C2 --> C3
    end

    subgraph P4 [Phase 4 · Sphinx Automation & Generation]
        D1[sphinx-apidoc:<br/>generate .rst from source]
        D2[sphinx-build with autodoc:<br/>render HTML / PDF]
        D3[Publish generated documentation]
        D1 --> D2 --> D3
    end

    subgraph P5 [Phase 5 · Review & Maintenance]
        E1[Review generated docs for accuracy]
        E2{Docs correct & complete?}
        E1 --> E2
    end

    P1 --> P2 --> P3 --> P4 --> P5
    E2 -- yes --> Done([Published & maintained])
    E2 -- no, gaps found --> P1

    %% Documentation agent interaction points
    DA{{Documentation Agent}}
    DA -. identifies scope .-> A1
    DA -. analyzes code .-> B2
    DA -. writes docs .-> C1
    DA -. runs generation .-> D1
    DA -. reviews output .-> E1

    classDef agent fill:#2b6cb0,stroke:#1a365d,color:#ffffff,stroke-width:2px;
    class DA agent;
```

> The blue **Documentation Agent** node uses dotted edges to show where it participates in
> each phase of the workflow.

## Phase notes

| # | Phase | Purpose | Documentation agent involvement | Depends on |
|---|-------|---------|---------------------------------|------------|
| 1 | Scope Identification | Decide what code needs documentation and define the audience and goals. | Identifies the scope. | A documentation request. |
| 2 | File / Logic Analysis | Read the in-scope source, understand its behavior, and find undocumented logic. | Analyzes the code. | Scope from Phase 1. |
| 3 | Inline Documentation Application | Add docstrings and inline comments in a consistent style. | Writes the documentation. | Analysis from Phase 2. |
| 4 | Sphinx Automation & Generation | Generate `.rst` stubs and build rendered HTML/PDF from docstrings, then publish. | Runs the generation. | Inline docs from Phase 3. |
| 5 | Review & Maintenance | Verify accuracy and completeness; loop back when gaps are found. | Reviews the output. | Generated docs from Phase 4. |

## Sequence & dependency summary

- **Linear flow:** Phase 1 → 2 → 3 → 4 → 5, with each phase depending on the output of the one before it.
- **Feedback loop:** if review finds the documentation inaccurate or incomplete, the workflow returns to scope identification for another pass.

## Rendering to PNG / PDF

The Mermaid block above is the editable source. To export a static image:

```bash
# PNG
npx @mermaid-js/mermaid-cli -i docs/documentation-agent/workflow-generic.md -o docs/documentation-agent/workflow-generic.png

# PDF
npx @mermaid-js/mermaid-cli -i docs/documentation-agent/workflow-generic.md -o docs/documentation-agent/workflow-generic.pdf
```

In VS Code, the Markdown preview renders the diagram directly, and the Mermaid
extension offers a right-click **Export** to PNG/SVG.
