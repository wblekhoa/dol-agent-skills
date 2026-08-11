import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const skill = fs.readFileSync(path.join(root, "SKILL.md"), "utf8");
const manifest = JSON.parse(fs.readFileSync(path.join(root, "skill-package.json"), "utf8"));
const cases = JSON.parse(fs.readFileSync(path.join(root, "evals/trigger-cases.json"), "utf8"));

assert.match(skill, /^---\nname: deep-research\n/);
for (const heading of ["Ground the host project", "Build a source plan", "Counter-review and verify", "Output contract"]) {
  assert.match(skill, new RegExp(`##[^\\n]*${heading}|###[^\\n]*${heading}`));
}
assert.equal(manifest.name, "deep-research");
assert.equal(manifest.compatibility.format, "agentskills.io");
assert.deepEqual(Object.keys(manifest.compatibility.adapters).sort(), ["claude-code", "codex", "gemini-cli", "hermes", "openclaw"]);
assert.equal(cases.length, 20);
assert.equal(cases.filter((entry) => entry.expected === "USE").length, 10);
assert.equal(cases.filter((entry) => entry.expected === "DO_NOT_USE").length, 10);
assert.equal(new Set(cases.map((entry) => entry.id)).size, cases.length);

for (const marker of manifest.publication.private_markers) {
  assert.equal(skill.includes(marker), false, `portable SKILL.md contains private marker: ${marker}`);
}

console.log("deep-research package verify PASS · 20 balanced trigger cases");
