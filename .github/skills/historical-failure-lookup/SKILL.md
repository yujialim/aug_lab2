---
name: historical-failure-lookup
description: "Search past incidents, closed bug reports, prior pull requests, and post-mortems for signatures that match a current failure or a proposed change. Use to bring in prior art before hypothesizing a cause, drafting requirements for a re-occurring area, or refactoring code with a regression history."
---

# Historical Failure Lookup

## When to use
- The Debugging Agent has a stack trace or error signature and wants to know if it has been seen before.
- The Requirements Agent is scoping work in an area with a history of unclear specs or regressions.
- The Refactoring Agent needs to assess risk before touching a fragile module.

## Inputs
- A **signature**: an exception type + message, a failing test name, an affected file, or a short description of the concern (required).
- Access to the historical corpus: `CHANGELOG.md`, `docs/postmortems/`, `docs/adr/`, closed issues and PRs (if provided as text), and the repository's git history.
- Optional: a time window (e.g., "last 12 months").

## Procedure

1. **Canonicalize the signature.** Reduce the signature to a small set of high-signal tokens: the exception class, the last in-repo frame's function name, the module path. Discard timestamps, IDs, and quoted user data.
2. **Search the corpus.** Match canonical tokens against changelog entries, post-mortems, ADRs, issue/PR text, and commit messages. Prefer exact matches on exception class and function name.
3. **Score matches.** For each hit, score by: same exception class (+2), same function or file (+2), same root cause described (+3), same fix pattern (+1). Discard hits scoring below a threshold.
4. **Extract the outcome.** For each surviving match, record what the resolution was: code fix (with commit ref if available), config change, spec change, "won't fix", or "still open".
5. **Detect repeat offenders.** If the same file or function appears in ≥3 matches, mark the area as **high-risk** and surface that at the top of the report.

## Output format

- `signature`: the canonicalized token set that was searched.
- `matches`: `[{source, id_or_ref, title, score, outcome, date}]` ordered by score.
- `high_risk_areas`: files or functions with ≥3 historical failures, with counts.
- `no_match`: `true` if nothing above threshold was found (the caller should treat the failure as novel).

## Consumed by
Debugging Agent, Refactoring Agent, Requirements Agent.

## Will not do
- Query external bug trackers over the network. The corpus is whatever the caller provides.
- Reopen or comment on historical issues.
- Speculate about causes that are not supported by a matched historical record.
