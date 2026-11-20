"use strict";
/*
 * CostWarden Hard-Limit Audit — pure scoring logic.
 * No DOM, no network. Answers are plain data; nothing is ever sent anywhere.
 * Exported for Node tests when `module` exists; also attached to window.
 */

// Each question: id, text, provider scope ("all" or list), and options.
// Each option has a risk weight: 0 = safe, 1 = partial, 2 = risky.
// `fix` is shown in the result checklist when risk > 0.
var AUDIT_QUESTIONS = [
  {
    id: "provider",
    text: "Which do you spend the most on?",
    scope: "all",
    options: [
      { label: "OpenAI API", value: "openai", risk: 0 },
      { label: "Anthropic API", value: "anthropic", risk: 0 },
      { label: "OpenRouter", value: "openrouter", risk: 0 },
      { label: "Coding agents (Claude Code / Codex / Cursor)", value: "agents", risk: 0 }
    ]
  },
  {
    id: "hard_limit_set",
    text: "Have you set a hard spending limit (the kind that actually stops requests), not just a soft budget alert?",
    scope: "all",
    fix: "Turn on the enforceable hard limit in your provider's billing settings — a soft budget only emails you while spending continues.",
    options: [
      { label: "Yes, a hard limit is set", value: "yes", risk: 0 },
      { label: "Only a soft budget / alert", value: "soft", risk: 2 },
      { label: "No limit at all", value: "no", risk: 2 },
      { label: "I don't know", value: "unknown", risk: 1 }
    ]
  },
  {
    id: "limit_verified_on",
    text: "Have you personally verified the limit is ON? (Provider hard caps ship opt-in and off by default.)",
    scope: "all",
    fix: "Open the billing/limits page yourself and confirm the cap is enabled — defaults leave it off.",
    options: [
      { label: "Yes, I checked it myself", value: "yes", risk: 0 },
      { label: "I set it once but never re-checked", value: "once", risk: 1 },
      { label: "No / not sure", value: "no", risk: 2 }
    ]
  },
  {
    id: "limit_scope",
    text: "Is the limit applied per project / workspace, or only as one org-wide total?",
    scope: "all",
    fix: "Add per-project (OpenAI) or per-workspace (Anthropic) limits so one project can't consume the whole org budget.",
    options: [
      { label: "Per project / workspace", value: "per_project", risk: 0 },
      { label: "Org-wide only", value: "org", risk: 1 },
      { label: "No limit, so no scope", value: "none", risk: 2 }
    ]
  },
  {
    id: "daily_cap",
    text: "Do you have any DAILY cap or daily check on AI spend?",
    scope: "all",
    fix: "A monthly cap alone lets a runaway loop burn the whole month in one night. Add a daily check (even a 5-minute poll of the usage API) or a self-hosted guard.",
    options: [
      { label: "Yes, daily cap or daily automated check", value: "yes", risk: 0 },
      { label: "I eyeball it most days", value: "manual", risk: 1 },
      { label: "No — monthly view only", value: "no", risk: 2 }
    ]
  },
  {
    id: "alert_destination",
    text: "When spend crosses ~80% of budget, does an alert land somewhere you actually look every day (Slack, phone, primary inbox)?",
    scope: "all",
    fix: "Route budget alerts to Slack or your primary inbox — an alert in a billing portal you never open is not an alert.",
    options: [
      { label: "Yes, Slack / phone / main inbox", value: "yes", risk: 0 },
      { label: "Email to an address I rarely check", value: "rare", risk: 1 },
      { label: "No alerts set", value: "no", risk: 2 }
    ]
  },
  {
    id: "agent_keys_separate",
    text: "Do automated scripts / AI agents use separate API keys from the ones you use interactively?",
    scope: "all",
    fix: "Give agents their own keys. A leaked or repurposed personal key bypasses every per-key limit you set.",
    options: [
      { label: "Yes, separate keys for agents", value: "yes", risk: 0 },
      { label: "Some do, some share", value: "some", risk: 1 },
      { label: "Everything shares one key", value: "shared", risk: 2 }
    ]
  },
  {
    id: "auto_kill",
    text: "If a key started burning $100/hour at 3am, is there anything that would stop it automatically?",
    scope: "all",
    fix: "Set up automatic key disabling on budget breach (provider feature or a self-hosted watcher). Human reaction time is the most expensive line item.",
    options: [
      { label: "Yes, auto-disable is wired up", value: "yes", risk: 0 },
      { label: "A hard provider cap would eventually stop it", value: "cap", risk: 1 },
      { label: "No — it would run until I notice", value: "no", risk: 2 }
    ]
  },
  {
    id: "know_last_month",
    text: "Do you know, roughly, what you actually spent on AI APIs last month?",
    scope: "all",
    fix: "Check last month's real total in each provider's usage dashboard and write it down — you can't cap what you haven't measured.",
    options: [
      { label: "Yes, within ~10%", value: "yes", risk: 0 },
      { label: "Rough guess", value: "guess", risk: 1 },
      { label: "No idea", value: "no", risk: 2 }
    ]
  },
  {
    id: "multiple_providers",
    text: "Do you pay more than one AI provider (e.g. OpenAI + Anthropic + OpenRouter)?",
    scope: "all",
    fix: "Each provider has its own limits page. Audit every one — the un-capped second provider is the usual hole.",
    options: [
      { label: "No, just one provider", value: "one", risk: 0 },
      { label: "Yes, and every one has limits set", value: "all_capped", risk: 0 },
      { label: "Yes, and only some have limits set", value: "some", risk: 2 }
    ]
  },
  {
    id: "agent_spend_visibility",
    text: "Can you see what your coding agents (Claude Code / Codex / Cursor) spent yesterday, separately from your app's API spend?",
    scope: "all",
    fix: "Give coding agents dedicated keys/projects so their spend is attributable — agent loops are the source of nearly every 2026 bill-shock story.",
    options: [
      { label: "Yes, agent spend is separate and visible", value: "yes", risk: 0 },
      { label: "It's all mixed into one total", value: "mixed", risk: 1 },
      { label: "I don't use coding agents", value: "na", risk: 0 },
      { label: "No visibility at all", value: "no", risk: 2 }
    ]
  },
  {
    id: "fallback_plan",
    text: "If you got a $500 surprise bill tomorrow, do you know the exact clicks to freeze all AI spend within 5 minutes?",
    scope: "all",
    fix: "Write down your freeze procedure now (which page, which keys to disable). During an incident is the worst time to figure it out.",
    options: [
      { label: "Yes, I know the steps", value: "yes", risk: 0 },
      { label: "I'd figure it out", value: "figure", risk: 1 },
      { label: "No", value: "no", risk: 2 }
    ]
  }
];

// answers: { questionId: value }
function scoreAudit(answers) {
  var totalRisk = 0;
  var maxRisk = 0;
  var fixes = [];
  AUDIT_QUESTIONS.forEach(function (q) {
    if (q.id === "provider") return;
    maxRisk += 2;
    var value = answers[q.id];
    var opt = null;
    q.options.forEach(function (o) { if (o.value === value) opt = o; });
    if (!opt) { totalRisk += 2; if (q.fix) fixes.push({ question: q.id, fix: q.fix }); return; }
    totalRisk += opt.risk;
    if (opt.risk > 0 && q.fix) fixes.push({ question: q.id, fix: q.fix });
  });
  var level;
  if (totalRisk <= 3) level = "Protected";
  else if (totalRisk <= 10) level = "Exposed";
  else level = "Critical";
  return { totalRisk: totalRisk, maxRisk: maxRisk, level: level, fixes: fixes };
}

var AUDIT_API = { AUDIT_QUESTIONS: AUDIT_QUESTIONS, scoreAudit: scoreAudit };
if (typeof module !== "undefined" && module.exports) module.exports = AUDIT_API;
if (typeof window !== "undefined") window.CWAudit = AUDIT_API;
