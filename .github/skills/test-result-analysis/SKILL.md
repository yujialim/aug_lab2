---
name: test-result-analysis
description: "Parse and interpret test output from pytest, unittest, JUnit XML, or generic CI logs. Use to extract the list of failing tests, classify each failure (assertion, error, timeout, flake, skip), locate the assertion site in source, and produce a compact baseline that other agents can compare against after a change."
---

# Test Result Analysis

## When to use
- A test run has completed (locally or in CI) and an agent needs to know **what failed and why** without re-running the suite.
- An agent needs a **baseline** snapshot before making a change, so it can prove parity or regression afterwards.
- A failing test must be reduced to a single assertion, file, and line before deeper debugging.

## Inputs
- One of: `pytest` stdout, `unittest` output, JUnit XML, or a CI log containing test output (required).
- The repository root, for resolving reported file paths to real source files.

## Procedure

1. **Identify the format.** Look for JUnit XML (`<testsuite>` root), pytest markers (`FAILED`, `PASSED`, `= short test summary info =`), unittest markers (`FAIL:`, `ERROR:`, `ok`), or generic patterns.
2. **Extract totals.** Record counts of `passed`, `failed`, `errored`, `skipped`, `xfailed`, `xpassed`. If a count cannot be determined, mark it `unknown` — do not guess.
3. **Extract each failing case.** For every failure, capture:
   - Fully qualified test name.
   - Failure class: `assertion`, `exception`, `timeout`, `collection_error`, `skip_unexpected`.
   - The final assertion or exception message.
   - The last frame in the stack that is inside the repository (ignore library frames).
   - File path and line number of that frame.
4. **Detect likely flakes.** Flag a test as `possibly_flaky` if the same test both passed and failed in the same output, or if the failure message mentions timing, ordering, network, or randomness.
5. **Produce the baseline object** (see output).

## Output format

Return a single object with these fields:

- `totals`: `{passed, failed, errored, skipped, xfailed, xpassed}`.
- `failures`: list of `{test_name, failure_class, message, file, line, possibly_flaky}`.
- `skipped_unexpected`: tests that were skipped but should not have been (e.g., skipped due to import error).
- `notes`: free-text observations (e.g., "collection failed before any test ran").

## Consumed by
Feature Agent, Debugging Agent, Refactoring Agent, Requirements Agent.

## Will not do
- Re-run the test suite.
- Modify test code.
- Diagnose the root cause of a failure — that is the Debugging Agent's job. This skill only reports **what failed**, not **why**.
