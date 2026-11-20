"use strict";
/* Audit UI: one question at a time, all state in memory only. */
(function () {
  var Q = window.CWAudit.AUDIT_QUESTIONS;
  var answers = {};
  var idx = 0;
  var app = document.getElementById("audit-app");
  var DOC_LINKS = {
    openai: { label: "OpenAI: usage limits & budgets (official docs)", url: "https://platform.openai.com/docs/guides/rate-limits" },
    anthropic: { label: "Anthropic: rate & spend limits (official docs)", url: "https://docs.claude.com/en/api/rate-limits" },
    openrouter: { label: "OpenRouter: limits & credits (official docs)", url: "https://openrouter.ai/docs/limits" },
    agents: { label: "OpenAI: usage limits & budgets (official docs)", url: "https://platform.openai.com/docs/guides/rate-limits" }
  };

  function render() {
    if (idx >= Q.length) return renderResult();
    var q = Q[idx];
    var html = '<p class="progress">Question ' + (idx + 1) + " of " + Q.length + "</p>";
    html += "<h2>" + q.text + "</h2><div class=\"options\">";
    q.options.forEach(function (o) {
      html += '<button type="button" class="opt" data-v="' + o.value + '">' + o.label + "</button>";
    });
    html += "</div>";
    if (idx > 0) html += '<p><button type="button" id="back">← Back</button></p>';
    app.innerHTML = html;
    app.querySelectorAll(".opt").forEach(function (b) {
      b.addEventListener("click", function () {
        answers[q.id] = b.getAttribute("data-v");
        idx += 1;
        render();
      });
    });
    var back = document.getElementById("back");
    if (back) back.addEventListener("click", function () { idx -= 1; render(); });
  }

  function renderResult() {
    var r = window.CWAudit.scoreAudit(answers);
    var provider = answers.provider || "openai";
    var doc = DOC_LINKS[provider] || DOC_LINKS.openai;
    var html = '<p class="progress">Done — ' + Q.length + " questions</p>";
    html += '<div class="verdict verdict-' + r.level.toLowerCase() + '"><h2>' + r.level +
      '</h2><p>Risk score: ' + r.totalRisk + " / " + r.maxRisk + "</p></div>";
    if (r.fixes.length) {
      html += "<h3>Fix these, in order</h3><ol>";
      r.fixes.forEach(function (f) { html += "<li>" + f.fix + "</li>"; });
      html += "</ol>";
    } else {
      html += "<p>No gaps found. Keep re-checking after any provider changes its billing defaults.</p>";
    }
    html += '<p>Official reference: <a href="' + doc.url + '" rel="noopener">' + doc.label + "</a></p>";
    html += "<p>Fixing the checklist closes today's holes. The one thing a checklist can't do is watch spend daily and stop a key at 3am — that's what the self-hosted Guard Kit automates.</p>";
    html += '<p><a class="cta" href="/kit/">See the Guard Kit — $59 one-time</a></p>';
    html += '<p class="privacy">This audit ran entirely in your browser. Nothing was sent or stored.</p>';
    html += '<p><button type="button" id="restart">Start over</button></p>';
    app.innerHTML = html;
    document.getElementById("restart").addEventListener("click", function () {
      answers = {}; idx = 0; render();
    });
  }

  render();
})();
