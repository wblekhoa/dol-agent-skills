---
name: audit-codex-storage
description: Use when Codex storage under ~/.codex is unexpectedly large, disk space is low, sessions or generated media need cleanup, or Codex/ChatGPT appears to consume excessive application memory.
---

# Audit Codex Storage

Audit first, preserve resumability, and separate disk pressure from process memory. Never infer that old or large data is disposable.

## Workflow

1. Resolve `CODEX_HOME` as `${CODEX_HOME:-$HOME/.codex}`. Read its `AGENTS.md` and any local retention workflow or policy before running commands.
2. Capture `df`, category sizes, largest items, and Codex/ChatGPT RSS. Do not install dependencies or modify product repositories.
3. Prefer the machine's deterministic planner when both `scripts/storage_retention.py` and its policy exist:

```bash
python3 "$CODEX_HOME/scripts/storage_retention.py" audit --strict
```

Read the generated JSON plan even when strict mode exits non-zero. Report the exact `high` or `critical` evidence, plan path, and hash.

4. If no local planner exists, run the bundled read-only fallback:

```bash
python3 <skill-dir>/scripts/audit_codex_storage.py \
  --root "${CODEX_HOME:-$HOME/.codex}" --strict
```

The fallback inventories storage and RSS but deliberately emits zero reclaimable bytes. Do not invent deletion candidates from its largest-file list.

5. Read [references/decision-model.md](references/decision-model.md) before proposing or executing any mutation.
6. Inspect `execute_pending`, `manual_review`, `archived_review`, and `cold_review` items individually. Use task tools to ask the owning task about closure when available. Treat errors, missing titles, age, and size as review signals, never deletion proof.
7. Apply only explicitly approved action IDs from a fresh, unchanged, hash-bound plan. Never broaden approval from one item or category to another.
8. Re-run the audit and report logical reduction, filesystem free-space change, receipt paths, and anything retained.

## Hard Gates

- Never delete an entire task to remove heavy artifacts inside it.
- Never delete raw/paginated sessions, archived sessions, cold archives, SQLite history, or generated media based only on age or size.
- Never treat `execute_pending` as trash.
- Never run `rm -rf`, wildcard deletion, broad `find -delete`, manual database surgery, or unplanned move/quarantine/purge.
- Never claim disk cleanup fixes RAM. Compare equivalent idle workloads and investigate sustained RSS growth separately.
- Stop before mutation unless the current user explicitly approves the exact plan/action scope.

## Required Report

Report gate and exit code; disk/root pressure; category sizes/status; action counts/bytes; largest review and reclaim candidates; every pending/manual item; plan path/hash; current process RSS; executed actions; reclaimed bytes; retained blockers; and verification results.

## Verification

Run the skill's tests after changing its helper:

```bash
python3 -m unittest discover -s <skill-dir>/tests -p 'test_*.py' -v
python3 <skill-dir>/scripts/audit_codex_storage.py --help
```
