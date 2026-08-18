# Codex Storage Decision Model

Use this reference only after the read-only audit. Local policy and current measured evidence override these generic rules.

## Source Priority

1. Current user approval for an exact scope
2. Local `AGENTS.md` and retention policy
3. Fresh immutable plan plus action evidence
4. Apply and archive receipts
5. Task state, summaries, exports, pins, and writer locks
6. Generic rules in this skill

Never use an older report as current truth.

## Classification

| Result | Meaning | Allowed next step |
|---|---|---|
| `cold_archive_candidate` | Closed and summary-backed raw session | Lossless compression through the local executor after approval |
| `quarantine_candidate` | Closed, unreferenced media exceeds retained-set policy | Recoverable move after approval; count zero immediate reclaim |
| `delete_derived_candidate` | Clean project and lockfile prove a cache/build directory is rebuildable | Scoped deletion after approval |
| `delete_ephemeral_candidate` | Narrow known temporary pattern | Scoped deletion after approval |
| `purge_quarantine_candidate` | Grace-expired item already recorded in quarantine | Permanent purge only with separate approval |
| `execute_pending` | Work may be unfinished or unexported | Complete, export, pin, or record closure; do not delete |
| `manual_review` | Ownership or closure is not proven | Inspect without mutation |
| `archived_review` | App-archived history reached a review watermark | Inspect storage representation and resumability; never auto-delete |
| `cold_review` | Cold storage reached a review watermark | Propose a bounded retention decision; never auto-purge |

## Evidence Required Before Mutation

Require all applicable evidence:

- Fresh plan path and matching SHA-256
- Exact action ID and category
- Target path unchanged in size and modification time
- No active writer lock or running owner
- Terminal closure receipt where required
- Durable summary or export where required
- Pin/reference checks completed
- User approval names the action or narrowly bounded category
- Executor supports the action and emits a receipt

If one condition is unknown, route to review rather than cleanup.

## Protected Storage

Treat these as state, not cache:

- `sessions/`, `archived_sessions/`, `cold_sessions/`
- Thread-history, log, state, and metadata SQLite databases
- Paginated raw rollout files that contain child-task history
- Generated media without proven export/closure
- Dirty worktrees and visualization projects without a lockfile

Do not manually remove raw files while database rows still reference them.

## Disk Versus Memory

Disk metrics: category bytes, filesystem free space, logical versus compressed size, deleted-open files.

Memory metrics: per-process RSS, total RSS, memory pressure, idle baseline, growth under a repeatable workload.

Large disk history can increase indexing/startup work, but it does not prove a RAM leak. Restarting the app is an interruption requiring approval when active work may be lost.

## Report Template

```text
Gate / audit exit:
Plan path / SHA:
Disk free and Codex root:
Category pressure:
Action counts and bytes:
Largest reclaim candidates:
Review-only queues:
Execute-pending/manual items:
Current process RSS:
Approved actions executed:
Logical and filesystem bytes reclaimed:
Receipts:
Retained blockers and why:
Verification:
```
