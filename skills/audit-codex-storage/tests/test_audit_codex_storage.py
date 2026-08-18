import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
CLI = SKILL_ROOT / "scripts" / "audit_codex_storage.py"
NOW = "2026-08-18T10:00:00Z"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import audit_codex_storage as audit_helper


class AuditCodexStorageTests(unittest.TestCase):
    def run_cli(self, storage_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--root",
                str(storage_root),
                "--format",
                "json",
                "--no-processes",
                "--now",
                NOW,
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_file(self, root: Path, relative: str, size: int) -> Path:
        file_path = root / relative
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"x" * size)
        os.utime(file_path, (1_700_000_000, 1_700_000_000))
        return file_path

    def snapshot(self, root: Path) -> dict[str, tuple[int, int]]:
        return {
            str(file_path.relative_to(root)): (file_path.stat().st_size, file_path.stat().st_mtime_ns)
            for file_path in root.rglob("*")
            if file_path.is_file()
        }

    def test_inventory_is_read_only_and_covers_high_risk_categories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_root = Path(tmpdir)
            self.write_file(storage_root, "sessions/rollout.jsonl", 3)
            self.write_file(storage_root, "archived_sessions/rollout.jsonl", 5)
            self.write_file(storage_root, "cold_sessions/set/rollout.jsonl.zst", 7)
            self.write_file(storage_root, "generated_images/thread/image.png", 11)
            self.write_file(storage_root, "logs_2.sqlite", 13)
            before = self.snapshot(storage_root)

            result = self.run_cli(storage_root, "--top", "3")

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["mode"], "read_only")
            self.assertEqual(report["categories"]["sessions"]["bytes"], 3)
            self.assertEqual(report["categories"]["archived_sessions"]["bytes"], 5)
            self.assertEqual(report["categories"]["cold_sessions"]["bytes"], 7)
            self.assertEqual(report["categories"]["generated_images"]["bytes"], 11)
            self.assertEqual(report["categories"]["databases"]["bytes"], 13)
            self.assertEqual(report["safety"]["reclaimable_bytes"], 0)
            self.assertTrue(report["safety"]["requires_explicit_approval"])
            self.assertEqual(self.snapshot(storage_root), before)

    def test_strict_reports_before_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_root = Path(tmpdir)
            self.write_file(storage_root, "sessions/rollout.jsonl", 3)

            result = self.run_cli(storage_root, "--strict", "--minimum-free-percent", "100")

            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertIn(report["gate_status"], {"high", "critical"})
            self.assertGreater(report["pressure"]["disk_free_bytes"], 0)

    def test_detects_machine_specific_retention_owner_without_running_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_root = Path(tmpdir)
            self.write_file(storage_root, "scripts/storage_retention.py", 3)
            self.write_file(storage_root, "storage-retention.toml", 5)

            result = self.run_cli(storage_root)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["local_retention"]["available"])
            self.assertTrue(report["local_retention"]["policy_available"])
            self.assertFalse(report["local_retention"]["executed"])

    def test_process_memory_includes_descendant_tool_servers(self) -> None:
        process_table = """
100 1 100 /Applications/ChatGPT.app/Contents/MacOS/ChatGPT
101 100 200 codex app-server
102 101 300 node figma-console-mcp
200 1 400 unrelated-worker
"""

        report = audit_helper.summarize_process_table(process_table)

        self.assertEqual(report["direct_match_count"], 2)
        self.assertEqual(report["count"], 3)
        self.assertEqual(report["direct_match_rss_bytes"], 300 * 1024)
        self.assertEqual(report["total_rss_bytes"], 600 * 1024)
        self.assertEqual({item["pid"] for item in report["processes"]}, {100, 101, 102})


if __name__ == "__main__":
    unittest.main()
