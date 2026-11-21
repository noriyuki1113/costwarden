# Gumroad listing draft — CostWarden Guard Kit (preorder)

Prepared 2026-11-21. Create the product in the user's Gumroad account with this copy, then replace the placeholder URL `https://gumroad.com/l/REPLACE_WITH_GUARD_KIT_PREORDER` in the site (build_site.py source) with the real product URL, rebuild, and push.

## Product name
CostWarden Guard Kit — self-hosted AI spend guard (preorder)

## Price
$59 one-time (preorder)

## Summary (short description)
A self-hosted guard for your AI API spend. You deploy it to your own Cloudflare Worker in minutes: it checks your provider spend on a schedule, alerts your Slack when you approach your daily cap, and disables keys where the provider API allows it. Your API keys never leave your environment — there is no hosted service and we never see your keys.

## Description
**Why this exists**
Provider spending limits are opt-in and off by default, and most are monthly. A runaway script or coding agent can burn a month of budget in one night. The Guard Kit adds the missing daily layer — inside your own infrastructure.

**What you get**
- A Cloudflare Worker you deploy yourself (one-click deploy from a GitHub repo)
- Scheduled spend checks against your provider usage/billing APIs
- A daily cap you set, with Slack alerts at 80% and at the cap
- Automatic key disable where the provider API supports it; where it doesn't, an immediate high-priority alert instead
- Setup guide and FAQ (documentation-based support)

**What it is not**
- Not a hosted service: we run no servers, hold no API keys, and have no access to your accounts
- Not an observability platform or analytics dashboard

**Honest preorder terms**
This is a preorder to validate demand. If we don't reach 5 preorders in the validation window (two weeks from launch), all preorders are refunded in full and the Kit won't be built. Preorders can be cancelled for a full refund any time before release.

**Support**
Documentation and FAQ only, stated plainly: this is a solo-built, self-hosted tool. Updates are published as GitHub releases you can pull in at your own pace.

## Checkout / settings notes
- Enable preorder mode (charge on release) if available; otherwise standard sale with the refund terms above stated on the page.
- Do the one-time USPTO "COSTWARDEN" check before enabling real charges (agreed default, 2026-11-21).
