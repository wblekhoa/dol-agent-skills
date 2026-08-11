# Deep Research

Portable research workflow for decisions that need multiple current sources, comparison against a
host project, counter-review, and explicit uncertainty.

## Install

Choose one delivery mode:

1. **No install:** give your AI the public `SKILL.md` URL and ask it to decide whether the skill
   matches the current request before following it.
2. **Project install:** copy this package to `.agents/skills/deep-research/`. Claude Code uses the
   equivalent `.claude/skills/deep-research/` projection.
3. **Governed install:** when the host provides the Skill Supply Chain tool, preview `install`, apply
   it only after review, then run `doctor` against the same package and target workspace.

Do not install over an existing skill with the same name unless its owner and rollback path are known.

## Use

Example prompt:

```text
Use deep-research to evaluate <topic> for <project outcome>. Verify current claims, compare the
options against the host project, and return Adopt/Adapt/Reject/Defer with evidence and residual risk.
```

The skill should decline simple lookups, ordinary code review, and UI-only audits that have a narrower
workflow.

## Personalize

Keep this package portable. Put product policy, preferred sources, output language, risk tolerance,
and local commands in the consuming project's instructions or in an explicitly owned fork. Do not
hand-edit a receipt-owned installation.

Validate personalization with one task that should trigger the skill and one nearby task that should
not. Keep the portable trigger boundary unchanged unless the package itself is intentionally revised
and re-evaluated.

## Verify

Before relying on the skill:

- confirm the package audit and package-local verification receipt pass;
- confirm the installed files match their install receipt;
- start a fresh runtime session and verify the skill is actually discoverable;
- run one positive and one counterexample prompt using the target project's real instructions.

Filesystem presence proves projection only. It does not prove that a runtime discovered or selected
the skill.

## Compatibility

The portable source follows the Agent Skills format. It projects to Claude Code, Codex, Gemini CLI or
Antigravity, OpenClaw, and Hermes. Runtime discovery remains a host-specific precondition and must be
verified in a fresh target session.
