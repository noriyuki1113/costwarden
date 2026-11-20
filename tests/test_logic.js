"use strict";
/* Node tests for audit scoring + calculator math. Run: node tests/test_logic.js */
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { AUDIT_QUESTIONS, scoreAudit } = require("../assets/audit-logic.js");
const { computeCost } = require("../assets/calc-logic.js");

let passed = 0;
function check(name, fn) { fn(); passed++; console.log("ok -", name); }

// --- Audit structure ---
check("audit has exactly 12 questions", () => {
  assert.strictEqual(AUDIT_QUESTIONS.length, 12);
});

// Build answer sets by picking, per question, the min-risk / max-risk option.
function answersByRisk(pickMax) {
  const a = {};
  for (const q of AUDIT_QUESTIONS) {
    const sorted = [...q.options].sort((x, y) => x.risk - y.risk);
    a[q.id] = (pickMax ? sorted[sorted.length - 1] : sorted[0]).value;
  }
  return a;
}
function mixedAnswers() {
  // Safe on the big structural items, risky on daily visibility items.
  const a = answersByRisk(false);
  a.daily_cap = "no";            // risk 2
  a.alert_destination = "rare";  // risk 1
  a.auto_kill = "cap";           // risk 1
  a.know_last_month = "guess";   // risk 1
  a.fallback_plan = "figure";    // risk 1
  return a;
}

check("all-safe answers -> Protected", () => {
  const r = scoreAudit(answersByRisk(false));
  assert.strictEqual(r.totalRisk, 0);
  assert.strictEqual(r.level, "Protected");
  assert.strictEqual(r.fixes.length, 0);
});

check("all-risky answers -> Critical", () => {
  const r = scoreAudit(answersByRisk(true));
  assert.strictEqual(r.totalRisk, r.maxRisk);
  assert.strictEqual(r.level, "Critical");
  assert.ok(r.fixes.length >= 8, "expected many fixes, got " + r.fixes.length);
});

check("mixed answers -> Exposed", () => {
  const r = scoreAudit(mixedAnswers());
  assert.strictEqual(r.totalRisk, 6);
  assert.strictEqual(r.level, "Exposed");
});

// --- Calculator math vs hand calculation from data/prices.json ---
const prices = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "prices.json"), "utf8"));
function model(id) { return prices.models.find((m) => m.id === id); }

check("calculator: gpt-4o-mini, 2000 in / 500 out, 1000 req/day", () => {
  const m = model("gpt-4o-mini");
  assert.ok(m, "gpt-4o-mini must be in prices.json");
  // hand: per request = 2000*1.5e-7 + 500*6e-7 = 0.0003 + 0.0003 = 0.0006
  const expectedPerReq = 2000 * m.input_per_token + 500 * m.output_per_token;
  const r = computeCost(m, 2000, 500, 1000);
  assert.ok(Math.abs(r.perRequest - expectedPerReq) < 1e-12);
  assert.ok(Math.abs(r.perRequest - 0.0006) < 1e-9, "perRequest=" + r.perRequest);
  assert.ok(Math.abs(r.daily - 0.6) < 1e-9, "daily=" + r.daily);
  assert.ok(Math.abs(r.monthly - 18.0) < 1e-9, "monthly=" + r.monthly);
  console.log("   gpt-4o-mini:", JSON.stringify(r));
});

check("calculator: claude-sonnet-4-5, 10000 in / 2000 out, 100 req/day", () => {
  const m = model("claude-sonnet-4-5");
  assert.ok(m, "claude-sonnet-4-5 must be in prices.json");
  // hand: per request = 10000*3e-6 + 2000*1.5e-5 = 0.03 + 0.03 = 0.06
  const r = computeCost(m, 10000, 2000, 100);
  assert.ok(Math.abs(r.perRequest - 0.06) < 1e-9, "perRequest=" + r.perRequest);
  assert.ok(Math.abs(r.daily - 6.0) < 1e-9, "daily=" + r.daily);
  assert.ok(Math.abs(r.monthly - 180.0) < 1e-9, "monthly=" + r.monthly);
  console.log("   claude-sonnet-4-5:", JSON.stringify(r));
});

console.log("\nAll " + passed + " tests passed.");
