# DOL Agent Skills

Portable, verified AI skills that can be used without adopting the private DOL control plane.

This repository is the public incubator for skills that share one trust, licensing, and release
boundary. A package should move to its own repository only when it gains distinct maintainers,
security policy, runtime, release cadence, or contribution workflow.

## Available skills

| Skill | Use when | Version |
|---|---|---|
| [Deep Research](skills/deep-research/README.md) | A decision needs current multi-source evidence, comparison, and counter-review | 0.2.0 |
| [Audit Codex Storage](skills/audit-codex-storage/README.md) | Codex storage is unexpectedly large or disk/process-memory pressure needs a safe audit | 0.1.0 |

## Install

Clone the collection:

```sh
git clone https://github.com/wblekhoa/dol-agent-skills.git
```

Then copy only the package you need:

```sh
# Codex, Gemini CLI/Antigravity, or a configured OpenClaw/Hermes workspace
cp -R dol-agent-skills/skills/<skill-name> .agents/skills/<skill-name>

# Claude Code
cp -R dol-agent-skills/skills/<skill-name> .claude/skills/<skill-name>
```

Read the package README before installation. Filesystem placement does not prove runtime discovery;
start a fresh target-runtime session and verify one positive and one counterexample prompt.

## Verify

Each published package contains deterministic trigger and report-contract evaluation plus a
hash-bound verification receipt:

```sh
node skills/deep-research/evals/verify.mjs
node skills/audit-codex-storage/evals/verify.mjs
```

The receipt proves the published package passed its declared local checks. It does not claim native
auto-discovery by every agent runtime.

## Publication policy

- Public packages contain no private DOL paths, secrets, or host-specific policy.
- Every package declares owner, provenance, license, compatibility, trigger cases, and verification.
- Runtime copies are projections; the package under `skills/` is canonical.
- New or changed packages remain unpublished until their package and publication receipts pass.
- Private adapters stay in their private owner repository and are not mirrored here.

## License

Repository content is licensed under [MIT](LICENSE). See
[Third-Party Notices](THIRD_PARTY_NOTICES.md) for acknowledged influences.
