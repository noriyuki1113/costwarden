#!/usr/bin/env python3
"""CostWarden Phase 0 static site generator.

Zero dependencies: Python 3 standard library only. No Astro, no npm —
dependency upkeep is maintenance, and this project is run by one person
with a no-maintenance premise (see README.md).

Run: python3 fetch_data.py && python3 build_site.py
Output: dist/
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SITE = "https://costwarden.com"

# TODO: replace with the real Cloudflare Web Analytics token after the
# site is connected in the Cloudflare dashboard. Placeholder on purpose.
CF_ANALYTICS_TOKEN = "REPLACE_WITH_CLOUDFLARE_WEB_ANALYTICS_TOKEN"
# TODO: replace with the real Gumroad preorder URL once the product is
# created in the owner's Gumroad account. Placeholder on purpose.
GUMROAD_PREORDER_URL = "https://gumroad.com/l/REPLACE_WITH_GUARD_KIT_PREORDER"

CSS = """
:root{--ink:#16211c;--mut:#5a6a62;--acc:#0e7a4f;--bg:#fbfaf7;--card:#fff;--line:#e3e0d8}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}
.wrap{max-width:760px;margin:0 auto;padding:0 20px 64px}
header.site{display:flex;justify-content:space-between;align-items:center;padding:18px 0;border-bottom:1px solid var(--line);margin-bottom:32px}
.logo{font-weight:800;font-size:20px;color:var(--ink);text-decoration:none}
nav a{margin-left:16px;color:var(--mut);text-decoration:none;font-size:15px}
nav a:hover{color:var(--acc)}
h1{font-size:40px;line-height:1.15;margin:8px 0 12px}
h2{font-size:24px;margin-top:36px}
.lede{font-size:19px;color:var(--mut)}
.cta{display:inline-block;background:var(--acc);color:#fff;padding:12px 22px;border-radius:10px;text-decoration:none;font-weight:700;margin:8px 8px 8px 0}
.cta.secondary{background:#fff;color:var(--acc);border:2px solid var(--acc)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 22px;margin:16px 0}
.card h3{margin-top:0}
.small{font-size:13px;color:var(--mut)}
footer{border-top:1px solid var(--line);margin-top:48px;padding-top:16px;font-size:13px;color:var(--mut)}
.opt{display:block;width:100%;text-align:left;background:#fff;border:1.5px solid var(--line);border-radius:10px;padding:13px 16px;margin:8px 0;font-size:16px;cursor:pointer}
.opt:hover{border-color:var(--acc)}
.progress{color:var(--mut);font-size:14px}
.verdict{border-radius:12px;padding:16px 22px;color:#fff}
.verdict-protected{background:#0e7a4f}.verdict-exposed{background:#b97a0e}.verdict-critical{background:#b02a1e}
label{display:block;margin:14px 0 4px;font-weight:600}
input,select{width:100%;padding:10px;border:1.5px solid var(--line);border-radius:8px;font-size:16px;background:#fff}
#result{font-size:18px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin-top:20px}
code{background:#eef0ea;padding:1px 6px;border-radius:5px}
"""

FOOTER = f"""
<footer>
<p>CostWarden (.com) is not affiliated with any other service of a similar name.</p>
<p>Model prices: <a href="https://github.com/BerriAI/litellm">LiteLLM model_prices data</a> (MIT), fetched {{fetched}}. Prices change — always confirm in your provider's dashboard.</p>
<p>© CostWarden · A static site: no accounts, no tracking of your inputs, no server holding your data.</p>
</footer>"""


def page(title: str, desc: str, body: str, fetched: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — CostWarden</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}/">
<style>{CSS}</style>
{extra_head}
</head>
<body>
<div class="wrap">
<header class="site">
<a class="logo" href="/">🛡 CostWarden</a>
<nav><a href="/audit/">Audit</a><a href="/calculator/">Calculator</a><a href="/guides/openai-spending-limit/">Guide</a><a href="/kit/">Guard Kit</a></nav>
</header>
{body}
{FOOTER.replace('{fetched}', fetched)}
</div>
</body>
</html>
"""


def lp(fetched: str) -> str:
    body = """
<h1>Stop the $453 overnight bill.</h1>
<p class="lede">CostWarden checks whether your AI spending limits are actually on — and guards your daily AI budget without ever holding your API keys.</p>
<p><a class="cta" href="/audit/">Run the free Hard-Limit Audit</a>
<a class="cta secondary" href="/kit/">Get the Guard Kit — $59 one-time</a></p>
<p class="small">The audit takes ~2 minutes and runs entirely in your browser. Nothing is sent or stored.</p>

<h2>This keeps happening</h2>
<div class="card"><h3>$453 in one night</h3>
<p>In August 2026, a developer's coding-agent session hit its subscription limit, wrote a script that pulled the API key from <code>.env</code>, and called the metered API directly — 1,917 requests, 62.2M tokens, about $453 in a day, against a configured $600 limit that turned out to be <em>soft</em>: it alerted, it didn't stop anything.</p>
<p class="small">Source: <a href="https://dev.to/jamilxt/your-ai-agent-just-spent-453-while-you-slept-cap-it-before-it-happens-to-you-1nd1">dev.to post-mortem</a></p></div>
<div class="card"><h3>$1.3M in 30 days</h3>
<p>Peter Steinberger (OpenClaw) reported roughly 100 autonomous coding agents generating 603B tokens and $1,305,088.81 in OpenAI charges over 30 days (OpenAI covered it; ~$300k at standard, non-Fast pricing). Nobody designed that bill — it accumulated, one agent at a time.</p>
<p class="small">Source: <a href="https://costmon.com/runaway-bills/">CostMon runaway-bill catalogue</a></p></div>
<div class="card"><h3>The pattern, not the people</h3>
<p>Every documented case has the same shape: agents or loops, a shared or repurposed key, no per-agent ceiling, and billing data that lags hours behind the spend. Smart teams, missing guardrails.</p></div>

<h2>Why provider limits alone don't save you</h2>
<div class="card">
<p><strong>They ship off.</strong> Enforceable hard caps now exist at the major providers — but they are opt-in, and the default state is off.</p>
<p><strong>They're monthly.</strong> A monthly cap does nothing about tonight: a runaway loop can burn the entire month before breakfast.</p>
<p><strong>They're coarse.</strong> Org-level totals hide which project, key, or agent is spending — and some workspaces can't be capped at all.</p>
<p>That's why the free audit exists: it checks the settings you <em>think</em> you have.</p>
</div>

<h2>A warden that never holds your keys</h2>
<div class="card">
<p>Most monitoring tools ask you to hand a stranger your API keys and trust their servers. CostWarden's Guard Kit works the other way: it runs <strong>inside your own Cloudflare account</strong>, polls your providers, alerts your Slack at 50/80/100% of your daily budget, and disables a runaway key — while your keys never leave your infrastructure. We sell the kit; you run the warden.</p>
<p><a href="/kit/">How the Guard Kit works →</a></p>
</div>

<h2>FAQ</h2>
<div class="card"><h3>Is this the same as costwarden.io?</h3><p>No. CostWarden (.com) is not affiliated with any other service of a similar name. Different product, different people.</p></div>
<div class="card"><h3>Do you store my API keys or audit answers?</h3><p>No. The audit and calculator run entirely in your browser. The Guard Kit runs in your own Cloudflare account; your keys never reach us.</p></div>
<div class="card"><h3>What support is included?</h3><p>Documentation and an FAQ — that's it, by design. CostWarden is run by one person with no maintenance operation, which is exactly why it is built to need none: no servers of ours to go down, nothing of yours on them.</p></div>
<div class="card"><h3>What if the Kit doesn't ship?</h3><p>The Kit is built only if validation succeeds (5 preorders in the window). If it doesn't reach that bar, all preorders are refunded in full.</p></div>
<div class="card"><h3>Can a watcher actually stop a bill?</h3><p>Honestly: no outside watcher is a true hard stop, because provider billing data lags. A daily-capped watcher with automatic key disabling is an early-warning brake — it turns a $453 night into a $50 lesson. The only true pre-request block is a proxy, and we don't sell one.</p></div>
"""
    return page("Stop the $453 overnight bill",
                "CostWarden checks whether your AI spending limits are actually on — and guards your daily AI budget without ever holding your API keys.",
                body, fetched)


def audit_page(fetched: str) -> str:
    body = """
<h1>The Hard-Limit Audit</h1>
<p class="lede">12 questions, ~2 minutes. Find out whether your AI spending limits would actually stop a runaway bill — or just watch it happen.</p>
<p class="small">This audit runs entirely in your browser. Your answers are never sent anywhere, never stored, and there is no account.</p>
<div id="audit-app"><noscript><p>The audit needs JavaScript — it still runs 100% locally in your browser.</p></noscript></div>
<script src="/assets/audit-logic.js"></script>
<script src="/assets/audit-ui.js"></script>
"""
    return page("Hard-Limit Audit",
                "12 questions to check whether your OpenAI / Anthropic / OpenRouter spending limits are actually on.",
                body, fetched)


def calculator_page(fetched: str, prices: dict) -> str:
    data_json = json.dumps(prices)
    body = f"""
<h1>AI API cost calculator</h1>
<p class="lede">What a workload actually costs, per day and per month — computed locally from current list prices.</p>
<label for="model">Model</label>
<select id="model"></select>
<label for="inp">Input tokens per request</label>
<input id="inp" type="number" value="2000" min="0">
<label for="out">Output tokens per request</label>
<input id="out" type="number" value="500" min="0">
<label for="req">Requests per day</label>
<input id="req" type="number" value="1000" min="0">
<div id="result">…</div>
<p class="small">Prices: LiteLLM model_prices data (MIT), fetched {fetched}. List prices before discounts, caching, or batch pricing.</p>
<div class="card"><h3>Know what it costs. Now check whether anything stops it.</h3>
<p>A budget you calculated is not a budget that enforces itself. Run the 2-minute audit:</p>
<p><a class="cta" href="/audit/">Run the free Hard-Limit Audit</a></p></div>
<script id="price-data" type="application/json">{data_json}</script>
<script src="/assets/calc-logic.js"></script>
<script src="/assets/calc-ui.js"></script>
"""
    return page("AI API cost calculator",
                "Estimate daily and monthly OpenAI, Anthropic and other LLM API costs from current list prices.",
                body, fetched)


def guide_page(fetched: str) -> str:
    body = """
<h1>OpenAI spending limits: the hard limit most teams never turn on</h1>
<p class="small">Last checked: 2026-11-21 · Facts follow OpenAI's official documentation, linked throughout.</p>
<h2>Soft limits email you. Hard limits stop.</h2>
<p>OpenAI has two different mechanisms that are easy to confuse. A <strong>budget / soft limit</strong> sends an alert when you cross a threshold — spending continues. An <strong>enforceable spending limit</strong> rejects requests (HTTP 429) once the cap is hit. In 2026 OpenAI made the enforceable limit available at organization and project level — but it is <strong>opt-in and off by default</strong>. If you never opened that settings page, you do not have a hard limit.</p>
<h2>How to turn it on</h2>
<ol>
<li>Open your organization's <a href="https://platform.openai.com/settings/organization/limits">limits settings</a> (requires an owner/admin role).</li>
<li>Set a monthly hard limit for the organization — this is your outer wall.</li>
<li>Repeat per project: project-level limits stop one runaway project from eating the org budget. See <a href="https://platform.openai.com/docs/guides/rate-limits">OpenAI's rate &amp; usage limits documentation</a>.</li>
<li>Set alert thresholds well below the cap (50% / 80%) and route them somewhere you look daily.</li>
<li>Use separate API keys per project and per automation, so a limit — or a disable — can target exactly one workload.</li>
</ol>
<h2>The holes that remain</h2>
<div class="card">
<p><strong>Monthly ≠ nightly.</strong> The cap is monthly. A loop at 3am can spend the whole month before the cap notices a problem — it only stops at the full monthly amount.</p>
<p><strong>Enforcement isn't instant.</strong> Usage reporting lags, so spend can overshoot between checks.</p>
<p><strong>It only covers OpenAI.</strong> Your Anthropic, OpenRouter, and coding-agent spend lives behind different switches, in different dashboards.</p>
</div>
<p>That gap — daily, cross-provider, agent-aware — is what the <a href="/audit/">Hard-Limit Audit</a> checks and the <a href="/kit/">Guard Kit</a> watches.</p>
<p><a class="cta" href="/audit/">Run the free Hard-Limit Audit</a></p>
"""
    return page("OpenAI spending limits: the hard limit most teams never turn on",
                "Soft limits email you; hard limits stop requests. How to turn on OpenAI's enforceable spending limit — and the holes that remain.",
                body, fetched)


def kit_page(fetched: str) -> str:
    body = f"""
<h1>The Guard Kit</h1>
<p class="lede">A warden that runs in <em>your</em> Cloudflare account. Your keys never leave your infrastructure — because there is no CostWarden server to send them to.</p>
<div class="card"><h3>What it does</h3>
<ul>
<li>Deploys to your own Cloudflare Worker with a one-click Deploy button (~10 minutes)</li>
<li>Polls OpenAI, Anthropic and OpenRouter spend on your schedule</li>
<li>Alerts your Slack at 50% / 80% / 100% of the <strong>daily</strong> budget you set</li>
<li>At 100%, automatically disables the runaway key where the provider's API allows it — and where it doesn't, sends a maximum-urgency alert instead (no fake promises)</li>
<li>Configuration is environment variables only. No admin panel, no database, nothing to babysit</li>
</ul></div>
<div class="card"><h3>What it deliberately is not</h3>
<p>Not a hosted SaaS. Not a proxy — it cannot block a single request before it happens, and billing data lags at every provider, so treat it as a fast brake, not a wall. Not an observability platform: no traces, no evals, no dashboards you'll never open.</p></div>
<p><strong>Price: $59, one-time.</strong> No subscription.</p>
<p><a class="cta" href="{GUMROAD_PREORDER_URL}">Preorder the Guard Kit — $59</a></p>
<div class="card"><h3>The honest deal</h3>
<p><strong>Built only if it validates:</strong> if we don't reach 5 preorders in the validation window, all preorders are refunded and the Kit won't be built.</p>
<p><strong>Support:</strong> documentation and FAQ only. CostWarden is one person with no maintenance operation — the Kit is designed so it needs none: it runs on your Cloudflare account, on your schedule.</p>
<p><strong>Updates:</strong> published as releases; taking them is optional and always your choice.</p>
<p><strong>Refunds:</strong> preorders can be cancelled any time before release for a full refund.</p></div>
<p class="small">Not sure you need it yet? The free <a href="/audit/">Hard-Limit Audit</a> shows you exactly which holes the Kit would close.</p>
"""
    return page("The Guard Kit — a self-hosted AI spend warden",
                "A self-hosted daily budget guard for OpenAI, Anthropic and OpenRouter. Runs in your Cloudflare account; your keys never leave.",
                body, fetched)


def main() -> int:
    prices_path = ROOT / "data" / "prices.json"
    if not prices_path.exists():
        print("error: data/prices.json missing — run fetch_data.py first")
        return 1
    prices = json.loads(prices_path.read_text(encoding="utf-8"))
    fetched = prices.get("fetched", "unknown")

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    (DIST / "audit").mkdir()
    (DIST / "calculator").mkdir()
    (DIST / "guides" / "openai-spending-limit").mkdir(parents=True)
    (DIST / "kit").mkdir()

    for name in ("audit-logic.js", "audit-ui.js", "calc-logic.js", "calc-ui.js"):
        shutil.copy(ROOT / "assets" / name, DIST / "assets" / name)

    pages = {
        DIST / "index.html": lp(fetched),
        DIST / "audit" / "index.html": audit_page(fetched),
        DIST / "calculator" / "index.html": calculator_page(fetched, prices),
        DIST / "guides" / "openai-spending-limit" / "index.html": guide_page(fetched),
        DIST / "kit" / "index.html": kit_page(fetched),
    }
    for path, html in pages.items():
        path.write_text(html, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({len(html)} bytes)")
    print(f"build complete: {len(pages)} pages, prices fetched {fetched}, "
          f"{len(prices['models'])} models")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
