import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const skill = read("SKILL.md");
const readme = read("README.md");
const helper = read("scripts/audit_codex_storage.py");
const decisionModel = read("references/decision-model.md");
const manifest = JSON.parse(read("skill-package.json"));
const triggerCases = JSON.parse(read(manifest.verification.trigger_cases));
const reportCases = JSON.parse(read(manifest.verification.report_cases));

assert.match(skill, /^---\nname: audit-codex-storage\n/);
for (const heading of ["Workflow", "Hard Gates", "Required Report", "Verification"]) {
  assert.match(skill, new RegExp(`## ${heading}`));
}
for (const contract of [
  /Never infer that old or large data is disposable/,
  /Read the generated JSON plan even when strict mode exits non-zero/,
  /Never treat `execute_pending` as trash/,
  /Never claim disk cleanup fixes RAM/,
  /Stop before mutation unless the current user explicitly approves/,
]) {
  assert.match(skill, contract);
}
for (const contract of [
  /always reports zero reclaimable bytes/i,
  /Old age, large size,\s+or a failed task is never deletion proof/i,
  /may exit non-zero for high or critical pressure/i,
]) {
  assert.match(readme, contract);
}
for (const contract of [
  /Never use an older report as current truth/,
  /Do not manually remove raw files while database rows still reference them/,
  /Large disk history can increase indexing\/startup work, but it does not prove a RAM leak/,
]) {
  assert.match(decisionModel, contract);
}

assert.equal(manifest.name, "audit-codex-storage");
assert.equal(manifest.version, "0.1.0");
assert.equal(manifest.publication.decision, "PUBLIC");
assert.equal(manifest.compatibility.format, "agentskills.io");
assert.deepEqual(Object.keys(manifest.compatibility.adapters).sort(), ["claude-code", "codex", "gemini-cli", "hermes", "openclaw"]);

assert.equal(triggerCases.length, 20);
assert.equal(triggerCases.filter((entry) => entry.expected === "USE").length, 10);
assert.equal(triggerCases.filter((entry) => entry.expected === "DO_NOT_USE").length, 10);
assert.equal(new Set(triggerCases.map((entry) => entry.id)).size, triggerCases.length);

const requiredReportCategories = [
  "deletion-proof",
  "fallback-boundary",
  "metric-separation",
  "owner-state",
  "pending-work",
  "plan-integrity",
  "privacy-boundary",
  "strict-exit",
];
assert.equal(reportCases.length, requiredReportCategories.length);
assert.deepEqual([...new Set(reportCases.map((entry) => entry.category))].sort(), requiredReportCategories.sort());
assert.equal(new Set(reportCases.map((entry) => entry.id)).size, reportCases.length);
for (const entry of reportCases) {
  assert.match(entry.id, /^quality-[a-z0-9-]+$/);
  assert.ok(["medium", "high"].includes(entry.severity));
  assert.ok(Array.isArray(entry.evidence_packet) && entry.evidence_packet.length >= 2);
  assert.ok(Array.isArray(entry.required_behaviors) && entry.required_behaviors.length >= 2);
  assert.ok(Array.isArray(entry.forbidden_behaviors) && entry.forbidden_behaviors.length >= 2);
}

const publicText = [skill, readme, helper, decisionModel].join("\n");
for (const marker of manifest.publication.private_markers) {
  assert.equal(publicText.includes(marker), false, `portable package contains private marker: ${marker}`);
}
for (const mutationPattern of [
  /\bos\.remove\s*\(/,
  /\b(?:os\.)?unlink\s*\(/,
  /\bshutil\.rmtree\s*\(/,
  /\bPath\([^\n]*\)\.unlink\s*\(/,
  /\bos\.rename\s*\(/,
]) {
  assert.doesNotMatch(helper, mutationPattern);
}
assert.match(helper, /"reclaimable_bytes": 0/);
assert.match(helper, /"executed": False/);

const python = process.env.PYTHON || "python3";
const tests = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
  { cwd: root, encoding: "utf8" },
);
assert.equal(tests.status, 0, tests.stderr || tests.stdout);

const help = spawnSync(python, ["scripts/audit_codex_storage.py", "--help"], {
  cwd: root,
  encoding: "utf8",
});
assert.equal(help.status, 0, help.stderr || help.stdout);
assert.match(help.stdout, /Read-only inventory for Codex storage and process memory/);

console.log("audit-codex-storage package verify PASS · read-only helper · 20 balanced trigger cases · 8 safety cases");
