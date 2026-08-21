---
name: source-code-context
description: "Locate the code that matters for a task: definitions, callers, tests that exercise a symbol, and configuration that influences it. Use whenever an agent needs a bounded slice of the codebase before reading or editing, so it does not pull in unrelated files or miss related tests."
---

# Source Code Context

## When to use
- Before editing: gather the minimum set of files an agent must read to make a safe change.
- Before debugging: identify the symbol implicated by a stack trace, its callers, and the tests that already cover it.
- Before documenting: find every place a documented symbol is defined or referenced.

## Inputs
- A **seed**: a symbol name, a file path, a line reference, or a plain-language description of the concern (required).
- Repository root.
- Optional: language or framework hint (e.g., "python", "typescript-react").

## Procedure

1. **Resolve the seed.** Convert the seed into one or more concrete definitions (file + line + symbol). If the seed is ambiguous (multiple symbols share the name), list all candidates and stop for disambiguation.
2. **Collect definitions.** For each resolved symbol, record its declaration file and signature.
3. **Collect callers / references.** Find all in-repo usage sites. Cap at a reasonable number (e.g., 50) and record the count if truncated.
4. **Collect related tests.** Locate tests that import the symbol or its module, or whose names reference it.
5. **Collect configuration.** Identify config files (`*.toml`, `*.yaml`, `*.json`, `*.env*`, `settings.py`) that reference the symbol, its module, or a feature flag that gates it.
6. **Report unresolved edges.** Note dynamic dispatch, reflection, plugin registration, or string-based imports that this static pass cannot follow.

## Output format

- `seed`: the resolved definition(s).
- `definitions`: `[{symbol, file, line, signature}]`.
- `references`: `[{file, line, snippet}]` (truncated with a count if large).
- `related_tests`: `[{test_name, file}]`.
- `configuration`: `[{file, key_or_line}]`.
- `unresolved_edges`: free-text list of things a static pass cannot see.

## Consumed by
Feature Agent, Debugging Agent, Documentation Agent, Refactoring Agent, Requirements Agent.

## Will not do
- Modify any file.
- Load the entire repository into context. This skill is explicitly a **bounded slice**.
- Follow runtime-only edges (dynamic imports, network calls) — these are reported as unresolved edges instead.
