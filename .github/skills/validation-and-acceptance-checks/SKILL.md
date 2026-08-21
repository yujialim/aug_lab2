---
name: validation-and-acceptance-checks
description: "Turn acceptance criteria into concrete, checkable assertions and evaluate outputs (code changes, test runs, spec drafts) against them. Use to prove that a feature meets its criteria, that a refactor preserved behavior, or that a drafted requirement is actually testable."
---

# Validation and Acceptance Checks

## When to use
- The Requirements Agent has drafted acceptance criteria and needs to confirm each one is expressible as an observable check.
- The Feature Agent has finished implementing and must show that every criterion is covered by a test.
- The Refactoring Agent must prove that the post-change test suite is at least as strong as the baseline.

## Inputs
- A set of **acceptance criteria** (Given/When/Then, or a bullet list) — required.
- One of:
  - a proposed test skeleton (for the Requirements Agent),
  - a diff plus a test run (for the Feature Agent),
  - a baseline and post-change test run (for the Refactoring Agent).

## Procedure

1. **Normalize criteria.** Rewrite each criterion into the form `Given <state>, When <action>, Then <observable outcome>`. If a criterion has no observable outcome, mark it `not_testable` and stop for that item.
2. **Map to checks.** For each testable criterion, identify or propose one or more test cases that assert the outcome. Record the mapping `criterion_id → test_name(s)`.
3. **Evaluate coverage.**
   - **For Requirements**: confirm every criterion has at least one proposed check.
   - **For Feature**: confirm every criterion has at least one passing test in the current run.
   - **For Refactoring**: confirm every test that passed in the baseline also passes now, and that no test was silently removed or skipped.
4. **Report gaps.** List any criterion that is `not_testable`, unmapped, or mapped only to failing/skipped tests.
5. **Never edit the criteria or the tests.** This skill only validates; changes are the caller's responsibility.

## Output format

- `criteria`: `[{id, given, when, then, status}]` where status is `testable | not_testable`.
- `mapping`: `[{criterion_id, tests: [test_name]}]`.
- `coverage`: `{covered, uncovered, failing, skipped}` counts and lists.
- `parity` (Refactoring only): `{baseline_passing_now_failing, baseline_passing_now_skipped, new_tests, removed_tests}`.
- `verdict`: `pass | pass_with_gaps | fail`, with a one-sentence reason.

## Consumed by
Feature Agent, Refactoring Agent, Requirements Agent.

## Will not do
- Write tests. Test authorship belongs to the Feature Agent.
- Run tests. Test execution is the Refactoring or Feature Agent's responsibility (only they have `execute`).
- Rewrite acceptance criteria. Reword only enough to check testability; substantive changes go back to the Requirements Agent.
