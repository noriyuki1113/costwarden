# CostWarden — Phase 0 static site

Validation site for [costwarden.com](https://costwarden.com): a free
Hard-Limit Audit, an API cost calculator, one guide, and the Guard Kit
preorder page. Design: `~/workspace/costwarden_blueprint.md` ·
Spec: `~/workspace/costwarden_phase0_spec.md`

## Deliberate deviation from the spec: no Astro, no npm

The Phase 0 spec named Astro. This build instead uses a **zero-dependency
Python 3 standard-library-only static site generator** (`build_site.py`),
the same approach as the owner's evenspec project. Reason: the project's
founding premise is **one operator, no maintenance**. An npm dependency
tree is itself recurring maintenance (updates, vulnerabilities, breaking
changes). Python's standard library has no dependency tree to maintain,
and the generator is a single file the owner can read end to end.

## Architecture

```
fetch_data.py   LiteLLM model_prices JSON (MIT) -> data/prices.json (curated models only)
build_site.py   data/prices.json + page templates -> dist/ (5 static pages)
assets/         vanilla JS: audit-logic.js / calc-logic.js are pure & unit-tested;
                audit-ui.js / calc-ui.js are thin DOM layers
tests/          node tests/test_logic.js — audit scoring + calculator math
.github/workflows/update-prices.yml   weekly fetch -> rebuild -> commit on diff
```

- No server, no database, no accounts. Audit answers and calculator
  inputs are processed **only in the visitor's browser** and are never
  sent anywhere (stated on the pages themselves).
- Prices come only from the fetched LiteLLM data file. No LiteLLM
  `enterprise/` code is used anywhere (that directory is commercially
  licensed; the price data file is MIT).
- Cloudflare Web Analytics beacon is included with a **placeholder
  token** (`REPLACE_WITH_CLOUDFLARE_WEB_ANALYTICS_TOKEN` in
  `build_site.py`). Replace it after connecting the site in Cloudflare.
- The Gumroad preorder button points to a **placeholder URL**
  (`GUMROAD_PREORDER_URL` in `build_site.py`). Replace after the product
  exists.

## Local build & test

```bash
python3 fetch_data.py     # refresh data/prices.json from LiteLLM
python3 build_site.py     # generate dist/
node tests/test_logic.js  # audit scoring + calculator tests
python3 -m http.server -d dist 8000   # preview at http://localhost:8000
```

## Deploy to Cloudflare Pages (owner's account, one-time)

1. Create the GitHub repository and push this directory (done by the
   owner — this repo intentionally has no remote configured by tooling).
2. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to
   Git → select the repository.
3. Build settings: build command `python3 fetch_data.py && python3 build_site.py`,
   output directory `dist`.
4. Add the custom domain `costwarden.com` and follow the DNS steps
   Cloudflare shows.
5. Enable Web Analytics for the domain and replace the placeholder
   beacon token in `build_site.py`, then rebuild/redeploy.
6. The weekly GitHub Action keeps prices fresh; a push to the repo
   triggers a Pages redeploy automatically.

## Gumroad preorder setup (owner's account, one-time)

1. Create a Gumroad account / product: "CostWarden Guard Kit — Preorder",
   price **$59**, product description copied from `dist/kit/index.html`
   (including the honest terms: built only at 5+ preorders, full refunds
   if it doesn't validate, docs-and-FAQ support only).
2. Set the product to preorder mode with cancellation allowed before release.
3. Copy the product URL into `GUMROAD_PREORDER_URL` in `build_site.py`
   and rebuild.
4. Before the first real charge: do the one-time USPTO check for
   COSTWARDEN (per the blueprint — not yet done).

## Operations

- Monthly checklist: see §5 of `~/workspace/costwarden_blueprint.md`
  (site up, Actions ran, sales/refunds, audit completions, provider
  limit changes, repeated FAQ questions).
- Support boundaries: documentation and FAQ only — stated on the site.
  No individual support, no onboarding, no SLA. The product is designed
  to need no maintenance; if that ever stops being true, the correct
  move is to shrink the product, not to add operations.
- Validation gate: 2 weeks after launch — 100 audit completions **or**
  5 Kit preorders → build the Kit (Phase 1). Otherwise fix copy/inflow
  and re-judge once. See the blueprint §3.
