---
name: deep-research
description: Use when a decision needs multi-source research, comparison, and verification before adopting a product, technology, tool, framework, workflow, or knowledge claim. Produces an evidence-backed Adopt, Adapt, Reject, or Defer recommendation. Do not use for a simple lookup, single-page extraction, code review, or UI audit.
compatibility: Requires access to project files and either web search or direct source retrieval.
---

# Deep Research

Produce a decision that another person can audit. Research volume is not the outcome; the outcome is
the smallest well-supported recommendation that fits the host project.

## Use this skill when

- Comparing products, technologies, libraries, frameworks, workflows, or market options.
- Testing whether an external proposal should be adopted in a specific project.
- Investigating a complex knowledge claim whose answer depends on multiple current sources.
- Re-evaluating a previously rejected option because material new evidence may exist.

## Do not use this skill when

- The request is a simple current-fact lookup or one-page extraction.
- The task is code review, debugging, or implementation with no adoption decision.
- The task is a UI or accessibility audit; use the host project's UI audit workflow.
- The user already fixed the decision and only needs execution.

## Select depth

| Mode | Use when | Minimum evidence |
|---|---|---|
| Light | One narrow question with low consequence | Two credible sources, one primary when available |
| Standard | A tool, product, or technology decision | Three to five decision questions, five credible sources |
| Deep | Broad, costly, risky, or multi-domain adoption | Independent workstreams, counter-review, explicit residual uncertainty |

Default to Standard. Escalate only when decision risk or scope justifies the extra context.

## Workflow

### 0. Ground the host project

Read the narrowest local source of truth that can change the decision:

1. project instructions and owner docs;
2. active plans and current implementation or runtime evidence;
3. ADRs, decision logs, lessons, issues, and rejection trails;
4. existing skills, scripts, dependencies, and verification gates.

If a source is unavailable, state the precondition. Do not infer its contents from a handoff or an
older summary.

### 1. Lock the decision

State:

- the decision to make;
- the user or product outcome;
- constraints and non-goals;
- facts versus assumptions;
- what evidence would change the answer.

### 2. Decompose into decision questions

Use three to five questions that discriminate between options, such as capability fit, integration
cost, operational risk, maintainability, rights, and verification. Do not collect facts that cannot
change the decision.

### 3. Build a source plan

Prefer sources in this order:

1. current official documentation, specifications, source code, and release notes;
2. primary research or reproducible benchmarks;
3. maintained open-source repositories with inspectable code, tests, CI, and license;
4. credible practitioner evidence;
5. aggregators only for discovery, never as final proof.

For fast-moving claims, record the retrieval date. For important claims, use two independent sources
when practical and at least one primary source when one exists.

### 4. Retrieve and keep a claim ledger

For each material claim, record:

| Claim | Evidence | Source type | Retrieved | Confidence |
|---|---|---|---|---|

Never invent a URL, version, benchmark, quote, or source. Mark inaccessible or unsupported claims as
unverified instead of smoothing over the gap.

### 5. Compare against the host system

For every serious option, check:

- overlap with existing capability;
- fit with the current architecture and source of truth;
- installation, migration, security, privacy, and license impact;
- ongoing maintenance and context cost;
- rollback path and smallest useful pilot;
- deterministic or observable evidence that can verify success.

### 6. Decide

Use one of four verdicts:

- **Adopt**: fits now, has sufficient evidence, and has a safe implementation path.
- **Adapt**: useful core, but scope or integration must change.
- **Reject**: conflicts with the outcome, source of truth, evidence, or risk boundary.
- **Defer**: potentially useful, but the current trigger or evidence bar is not met.

Do not force every option into the plan. One clear recommendation is usually better than several
simultaneous pilots.

### 7. Counter-review and verify

Challenge the draft:

- What evidence contradicts the recommendation?
- Did sunk cost, novelty, star count, recency, or user-pleasing bias influence the choice?
- Which prior rejection was re-litigated without new evidence?
- Which claim lacks a primary source or current verification?
- Is a lighter native capability sufficient?

Re-open every material citation in Light mode, and at least three material citations in Standard or
Deep mode. Verify local paths or commands cited in the answer.
Use an independent reviewer for high-consequence Deep mode when the runtime supports one; otherwise
disclose that the counter-review was performed by the same agent.

## Output contract

Return:

1. decision and confidence;
2. criteria derived from this decision;
3. evidence-backed option comparison;
4. Adopt, Adapt, Reject, or Defer verdicts;
5. recommended pilot or next action with measurable acceptance criteria;
6. verified versus unverified claims;
7. residual risks and the trigger that would change the answer;
8. source links placed next to the claims they support.

Avoid raw search dumps, generic scoring criteria, and architecture additions that do not improve the
locked outcome.

## Quick invocation

```text
Use deep-research to evaluate <topic> for <project/outcome>. Ground in the local source of truth,
compare realistic alternatives, respect prior decisions, verify current claims, and return one
Adopt/Adapt/Reject/Defer recommendation with a bounded pilot and residual risks.
```
