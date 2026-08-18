# Audit Codex Storage

Portable, audit-first workflow for diagnosing oversized Codex storage and separating disk pressure
from Codex or ChatGPT process-memory pressure.

## Safety boundary

The bundled helper is read-only and always reports zero reclaimable bytes. It inventories storage,
largest files, filesystem pressure, and matching process-tree RSS. It never deletes, moves,
quarantines, purges, or applies a retention plan.

When a machine already provides a retention planner, the skill uses that planner for classification
and requires a fresh hash-bound plan plus explicit approval before any mutation. Old age, large size,
or a failed task is never deletion proof.

## Install

Clone the public collection, then copy this complete package so its helper and decision reference
remain available:

```sh
git clone https://github.com/wblekhoa/dol-agent-skills.git

# Codex, Gemini CLI/Antigravity, or a configured OpenClaw/Hermes workspace
cp -R dol-agent-skills/skills/audit-codex-storage .agents/skills/audit-codex-storage

# Claude Code
cp -R dol-agent-skills/skills/audit-codex-storage .claude/skills/audit-codex-storage
```

Do not install over an existing skill with the same name unless its owner and rollback path are
known. Start a fresh target-runtime session after installation to verify discovery.

## Use

```text
Use audit-codex-storage to run a read-only strict audit of my Codex storage. Report disk and category
pressure, action counts, the largest candidates, all pending/manual-review items, the plan path and
hash, and Codex/ChatGPT RSS. Do not mutate anything without my approval for exact action IDs.
```

If no local retention planner exists, run:

```sh
python3 scripts/audit_codex_storage.py --root "${CODEX_HOME:-$HOME/.codex}" --strict
```

The command may exit non-zero for high or critical pressure after printing a valid report. Read the
report before treating the command as failed.

## Personalize

Keep machine-specific limits, retention categories, pin files, task tools, and mutation commands in
the host's policy or an explicitly owned fork. Do not weaken the portable hard gates. In particular,
preserve fresh-plan hashing, exact-action approval, resumability checks, and the disk-versus-memory
separation when adapting the skill to another agent runtime.

## Verify

```sh
node evals/verify.mjs
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/audit_codex_storage.py --help
```

The deterministic checks prove the fallback remains read-only and that the routing/report contracts
are present. They do not prove a specific machine's retention planner is safe or that an agent
runtime discovered the skill.

## Compatibility

The portable source follows the Agent Skills format. It projects to Claude Code, Codex, Gemini CLI
or Antigravity, OpenClaw, and Hermes. Process collection currently expects a Unix-like `ps` command;
storage inventory itself uses Python's cross-platform filesystem APIs.
