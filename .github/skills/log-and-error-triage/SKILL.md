---
name: log-and-error-triage
description: "Normalize raw logs and error messages, extract stack traces, deduplicate repeated events, and correlate error frames to source lines. Use when an agent has a log file, error dump, or exception message and needs a compact, cited summary before hypothesizing a cause or writing an error runbook."
---

# Log and Error Triage

## When to use
- An agent is handed a log file, console dump, or a single error message.
- The Debugging Agent needs a citable stack trace before forming hypotheses.
- The Documentation Agent needs to confirm that a runbook's documented error still occurs in the same form.

## Inputs
- Raw log text or an error message (required).
- Repository root, for resolving file paths in stack frames.
- Optional: a time window, if the log covers more than the incident.

## Procedure

1. **Normalize.** Strip ANSI codes, collapse repeated whitespace, and standardize timestamps to ISO-8601 if present.
2. **Segment by event.** Split the log into events, where an event is a timestamp + level + message (or a stack trace block).
3. **Deduplicate.** Group identical or near-identical messages; record `first_seen`, `last_seen`, and `count`. Near-identical means the message is the same after masking numbers, UUIDs, and quoted strings.
4. **Extract stack traces.** For each traceback, capture the exception type, exception message, and the full ordered list of frames. Mark each frame as `in_repo` or `external`.
5. **Correlate to source.** For every `in_repo` frame, verify the file exists at the reported path and record the referenced line's text.
6. **Rank events by severity and novelty.** Prefer `ERROR`/`CRITICAL` and events with `count == 1` in the window (novel), demote repeated `INFO`/`DEBUG` noise.

## Output format

- `summary`: one sentence describing the dominant failure mode, or "no errors found".
- `top_events`: ranked list of `{level, message, count, first_seen, last_seen}`.
- `stack_traces`: list of `{exception_type, message, frames: [{file, line, function, in_repo, source_line}]}`.
- `unresolved_frames`: frames whose file could not be located in the repository.
- `notes`: free-text observations (e.g., "log truncated mid-traceback").

## Consumed by
Debugging Agent, Documentation Agent.

## Will not do
- Guess at root cause.
- Fetch remote logs or connect to a log aggregator.
- Modify the log file.
