#!/usr/bin/env python3

from __future__ import annotations

import argparse
import heapq
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CATEGORY_ROOTS = {
    "sessions": "sessions",
    "archived_sessions": "archived_sessions",
    "cold_sessions": "cold_sessions",
    "generated_images": "generated_images",
    "generated_videos": "generated_videos",
    "visualizations": "visualizations",
    "attachments": "attachments",
    "worktrees": "worktrees",
    "storage_retention": "storage_retention",
}
ALL_CATEGORIES = (*CATEGORY_ROOTS, "databases", "other")
PROCESS_MARKERS = (
    "/Applications/ChatGPT.app",
    "/Applications/Codex.app",
    "/Applications/CodexBar.app",
    "codex app-server",
    "codex-code-mode-host",
    "Codex Computer Use.app",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only inventory for Codex storage and process memory.")
    parser.add_argument("--root", default=str(Path.home() / ".codex"), help="Codex storage root.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--top", type=int, default=12, help="Number of largest files to report.")
    parser.add_argument("--no-processes", action="store_true", help="Skip process RSS collection.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 for high or critical pressure.")
    parser.add_argument("--target-free-percent", type=float, default=20.0)
    parser.add_argument("--minimum-free-percent", type=float, default=15.0)
    parser.add_argument("--emergency-free-percent", type=float, default=10.0)
    parser.add_argument("--codex-soft-percent", type=float, default=10.0)
    parser.add_argument("--now", help="ISO timestamp for deterministic tests.")
    return parser.parse_args()


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def empty_stats() -> dict[str, Any]:
    return {"bytes": 0, "files": 0, "oldest_mtime": None, "newest_mtime": None}


def is_database(name: str) -> bool:
    lowered = name.lower()
    return any(token in lowered for token in (".sqlite", ".sqlite3", ".db-wal", ".db-shm")) or lowered.endswith(".db")


def category_for(relative: Path) -> str:
    if relative.parts:
        first = relative.parts[0]
        for category, root_name in CATEGORY_ROOTS.items():
            if first == root_name:
                return category
    if is_database(relative.name):
        return "databases"
    return "other"


def update_stats(stats: dict[str, Any], size: int, mtime: float) -> None:
    stats["bytes"] += size
    stats["files"] += 1
    stats["oldest_mtime"] = mtime if stats["oldest_mtime"] is None else min(stats["oldest_mtime"], mtime)
    stats["newest_mtime"] = mtime if stats["newest_mtime"] is None else max(stats["newest_mtime"], mtime)


def scan_storage(root: Path, top_count: int, now: datetime) -> tuple[dict[str, Any], list[dict[str, Any]], int, int, int]:
    categories = {name: empty_stats() for name in ALL_CATEGORIES}
    largest: list[tuple[int, str]] = []
    skipped = 0
    total_bytes = 0
    total_files = 0

    for current_root, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(current_root)
        dirnames[:] = [name for name in dirnames if not (current / name).is_symlink()]
        for name in filenames:
            file_path = current / name
            if file_path.is_symlink():
                continue
            try:
                file_stat = file_path.stat()
                relative = file_path.relative_to(root)
            except (OSError, ValueError):
                skipped += 1
                continue
            update_stats(categories[category_for(relative)], file_stat.st_size, file_stat.st_mtime)
            total_bytes += file_stat.st_size
            total_files += 1
            if top_count > 0:
                item = (file_stat.st_size, str(relative))
                if len(largest) < top_count:
                    heapq.heappush(largest, item)
                elif item > largest[0]:
                    heapq.heapreplace(largest, item)

    for stats in categories.values():
        oldest = stats["oldest_mtime"]
        newest = stats["newest_mtime"]
        stats["oldest_age_days"] = round(max(0.0, (now.timestamp() - oldest) / 86400), 1) if oldest else 0.0
        stats["newest_age_days"] = round(max(0.0, (now.timestamp() - newest) / 86400), 1) if newest else 0.0

    largest_items = [
        {"path": item_path, "bytes": size}
        for size, item_path in sorted(largest, key=lambda item: (-item[0], item[1]))
    ]
    return categories, largest_items, total_bytes, total_files, skipped


def summarize_process_table(process_table: str) -> dict[str, Any]:
    rows: dict[int, dict[str, Any]] = {}
    children: dict[int, list[int]] = {}
    for line in process_table.splitlines():
        parts = line.strip().split(maxsplit=3)
        if len(parts) != 4:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            rss_bytes = int(parts[2]) * 1024
        except ValueError:
            continue
        rows[pid] = {"pid": pid, "ppid": ppid, "rss_bytes": rss_bytes, "command": parts[3]}
        children.setdefault(ppid, []).append(pid)

    direct = {pid for pid, row in rows.items() if any(marker in row["command"] for marker in PROCESS_MARKERS)}
    selected = set(direct)
    pending = list(direct)
    while pending:
        parent = pending.pop()
        for child in children.get(parent, []):
            if child not in selected:
                selected.add(child)
                pending.append(child)

    processes = [rows[pid] for pid in selected]
    processes.sort(key=lambda item: item["rss_bytes"], reverse=True)
    return {
        "available": True,
        "count": len(processes),
        "direct_match_count": len(direct),
        "direct_match_rss_bytes": sum(rows[pid]["rss_bytes"] for pid in direct),
        "total_rss_bytes": sum(item["rss_bytes"] for item in processes),
        "processes": processes[:12],
    }


def process_memory() -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,rss=,command="],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        return {"available": False, "error": str(error), "processes": [], "total_rss_bytes": 0}
    return summarize_process_table(result.stdout)


def pressure_for(root: Path, root_bytes: int, args: argparse.Namespace) -> dict[str, Any]:
    usage = shutil.disk_usage(root)
    free_percent = usage.free / usage.total * 100 if usage.total else 0.0
    codex_percent = root_bytes / usage.total * 100 if usage.total else 0.0
    if free_percent < args.emergency_free_percent:
        status = "critical"
    elif free_percent < args.minimum_free_percent:
        status = "high"
    elif free_percent < args.target_free_percent or codex_percent >= args.codex_soft_percent:
        status = "advisory"
    else:
        status = "pass"
    return {
        "status": status,
        "disk_total_bytes": usage.total,
        "disk_free_bytes": usage.free,
        "disk_free_percent": round(free_percent, 2),
        "codex_root_bytes": root_bytes,
        "codex_percent_of_disk": round(codex_percent, 2),
    }


def build_report(root: Path, args: argparse.Namespace, now: datetime) -> dict[str, Any]:
    categories, largest_items, total_bytes, total_files, skipped = scan_storage(root, max(0, args.top), now)
    pressure = pressure_for(root, total_bytes, args)
    local_script = root / "scripts" / "storage_retention.py"
    local_policy = root / "storage-retention.toml"
    return {
        "schema_version": 1,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "mode": "read_only",
        "root": str(root),
        "gate_status": pressure["status"],
        "pressure": pressure,
        "total_files": total_files,
        "categories": categories,
        "largest_items": largest_items,
        "process_memory": {"available": False, "skipped": True, "processes": [], "total_rss_bytes": 0}
        if args.no_processes
        else process_memory(),
        "local_retention": {
            "available": local_script.is_file(),
            "script_path": str(local_script),
            "policy_available": local_policy.is_file(),
            "policy_path": str(local_policy),
            "executed": False,
        },
        "safety": {
            "reclaimable_bytes": 0,
            "requires_explicit_approval": True,
            "skipped_files": skipped,
            "protected_categories": ["sessions", "archived_sessions", "cold_sessions", "databases"],
            "note": "Inventory only. This helper never deletes, moves, quarantines, purges, or applies a retention plan.",
        },
    }


def human_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} TiB"


def print_text(report: dict[str, Any]) -> None:
    pressure = report["pressure"]
    print(f"Gate: {report['gate_status']} | mode: read_only")
    print(
        f"Disk free: {pressure['disk_free_percent']}% | "
        f"Codex: {human_bytes(pressure['codex_root_bytes'])} ({pressure['codex_percent_of_disk']}% of disk)"
    )
    for name, stats in report["categories"].items():
        print(f"- {name}: {human_bytes(stats['bytes'])}, {stats['files']} files")
    print("Largest files:")
    for item in report["largest_items"]:
        print(f"  {human_bytes(item['bytes'])} {item['path']}")
    memory = report["process_memory"]
    if memory.get("available"):
        print(
            f"Codex/ChatGPT process-tree RSS: {human_bytes(memory['total_rss_bytes'])} "
            f"across {memory['count']} processes "
            f"(direct matches: {human_bytes(memory['direct_match_rss_bytes'])})"
        )
    print("Reclaimable by this helper: 0 B; explicit approval is required for every mutation.")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"Root does not exist: {root}")
    now = parse_now(args.now)
    report = build_report(root, args, now)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    if args.strict and report["gate_status"] in {"high", "critical"}:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
