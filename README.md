# SBI Hub — Small Business Intelligence Hub

*Better Insights. Better Decisions. Stronger Businesses.*

A modular Streamlit application for small-business advisors. Build 1 delivers
the application shell and integrates the existing **Financial Modeler**
(Operating Model) as the first operational module.

## Modules

| Module | Status |
|---|---|
| Financial Modeler | **Active (Featured)** |
| Business Idea & Feasibility | Coming Soon |
| Business Valuation | Coming Soon |
| Workforce & Hiring | Coming Soon |
| Capital Investment | Coming Soon |
| Sales & Growth | Coming Soon |
| Operations Modeler | Coming Soon |
| Automation & AI Opportunity Evaluator | Coming Soon |

## Architecture

Modular monolith, single web service:

```
serve.py                      # Multi-app server: spawn both apps + reverse proxy
app.py                        # Hub entry point: page config, sidebar nav, view router
fm_app.py                     # Standalone Financial Modeler entry point (/fm)
sbi_hub/
├── shell/                    # Application shell
│   ├── landing.py            # Landing page + workspace placeholder views
│   ├── announcements.py      # Announcements loader + renderer
│   ├── theme.py              # Shell theme CSS + header bar (brand tokens)
│   └── icons.py              # Inline SVG icon set
├── config/
│   ├── branding.py           # Brand config (logo, org name, colors, artwork)
│   ├── modules.py            # Module registry (id, name, status, launch mode)
│   └── announcements.json    # Announcements config file
└── modules/
    └── financial_modeler/    # Vendored Financial Modeler (see below)
        ├── app.py            # render() entry called by the hub router
        ├── engine/           # Pure calculation engine (unchanged)
        ├── ui/               # Modeler screens (unchanged)
        ├── utils/            # Session, export, styles (unchanged)
        ├── analysis/  components/  config/  docs/  tests/
tests/                        # Hub-level + integration tests
.streamlit/config.toml        # Light theme, brand accent color
render.yaml                   # Render service definition
```

The hub is the central launcher. Sidebar nav buttons update
`st.session_state.active_view` inside a normal rerun (no page reloads, no
state loss), and `?view=<id>` remains supported as a deep-link entry
point. Sidebar workspace items — Recent Clients, Saved Scenarios,
Advisor Notes — render placeholder pages pending future builds.

Modules launch one of two ways, driven by the registry in
`sbi_hub/config/modules.py`:

- **`launch_url`** — standalone app opened in a new browser tab. The
  Financial Modeler uses this: `serve.py` runs it as its own Streamlit
  process at `/fm` with the original dark theme and independent session.
- **`entry_point`** — `"package.module:callable"` rendered embedded in
  the hub shell, for small tools that belong inside the workspace.

### One service, two apps

`serve.py` (the Render `startCommand`) spawns both Streamlit processes
and exposes them through a small aiohttp reverse proxy on `$PORT`:
`/fm*` -> Financial Modeler (`server.baseUrlPath=fm`, original dark
theme), everything else -> the hub (light theme). HTTP and WebSocket
traffic are proxied, including the `streamlit` subprotocol handshake.
Future standalone modules follow the same pattern: add a `fm_app.py`-style
entry script, spawn it in `serve.py` with its `baseUrlPath`, and give the
registry entry a `launch_url`.

## Branding

All sponsor/organization branding lives in `sbi_hub/config/branding.py`:
logo art, org name/subtitle, product name, app title, favicon, header
artwork, and the accent palette. The default is **North Star Consulting**
(navy + gold) with **Small Business Intelligence Hub** as the product
identity. Rebranding — e.g. to VtSBDC — means editing `BRAND` (and the
`primaryColor` in `.streamlit/config.toml`) only; components read the
config at render time. Neutral structure colors stay in `theme.py`.

## Financial Modeler integration

The Financial Modeler source (upstream `NSC-Rick/FinanceModeler` @ `49f2a0c`,
platform v0.9.3) is vendored under `sbi_hub/modules/financial_modeler/`.
The production repository, Render service, and user data are untouched.

Changes made during vendoring — none alter modeling logic:

- Imports rewritten from top-level (`from engine ...`) to package-qualified
  (`from sbi_hub.modules.financial_modeler.engine ...`).
- `app.py` wrapped in `render()`; `st.set_page_config` moved to the hub
  shell (it may only be called once per app).
- `utils/custom_styles.py` gained a one-line guard: its white-text alert
  override is skipped under the hub's light theme (the override targets the
  original dark theme's blue panels and would be unreadable on light
  backgrounds). Behavior under the dark theme is unchanged.
- A "← Back to SBI Hub" control is injected by the hub shell sidebar;
  all nine Financial Modeler screens, the session restore/autosave flow,
  scenario JSON save/load, Excel exports, and the AI coach widget are
  preserved as-is.

Saved-scenario compatibility: scenario files are user-side JSON; the
schema and validation (`engine/validation.py`) are unchanged, so existing
saved scenarios load identically. Session autosave still uses
`~/.finlite_session.json` and browser localStorage, independent per
deployment.

## Announcements

Managed via `sbi_hub/config/announcements.json` (title, description,
date, category, optional `pinned`). Rendered pinned-first, then
newest-first. An admin interface is a future enhancement.

## Running locally

```bash
pip install -r requirements.txt
python serve.py            # full stack: hub on /, modeler on /fm
```

Or run either app alone: `streamlit run app.py` (hub only) or
`streamlit run fm_app.py` (modeler only; its dark theme flags are applied
by `serve.py` in production).

## Deployment (Render)

`render.yaml` defines a free-tier Python web service:

- Build: `python -m pip install -r requirements.txt`
- Start: `python serve.py` (spawns hub + modeler, proxies `$PORT`)

## Testing

```bash
pytest
```

## Build 1 Validation Report

- **258 tests passing** (209 vendored Financial Modeler baseline tests +
  49 hub tests) covering engine calculations, P&L/cash-flow statements,
  loan amortization, capital stack, scenario JSON save/load validation,
  Excel export, module registry integrity (icon keys, entry-point
  resolution), announcement ordering, `?view=` deep-link handling,
  session-state preservation across navigation, and app-level navigation
  (landing → Financial Modeler → back to hub) via Streamlit `AppTest`.
- Browser-verified with Playwright: adding a revenue stream in the
  Financial Modeler, navigating Home, and re-entering preserves the data
  (`Revenue Streams: 1` before and after); scenario JSON save and Excel
  export downloads verified end-to-end.
- App boots clean: `streamlit run app.py` serves the landing page with all
  eight module cards; the Financial Modeler renders and returns to the hub.
- Synthetic data only; no real client data stored or migrated.

### Known limitations / risks

1. **Vendored code drift** — upstream Financial Modeler fixes must be
   re-vendored into `sbi_hub/modules/financial_modeler/` manually.
2. **Shared session state** — hub and module share `st.session_state`.
   Keys are namespaced by convention (`active_view` for the hub);
   future modules should use a `{module_id}__` prefix to avoid collisions.
3. **Single `set_page_config`** — the hub owns page config; module-level
   titles/icons now show "SBI Hub" in the browser tab.
4. **Session file scope** — `~/.finlite_session.json` is per-server-home;
   on ephemeral Render free-tier filesystems, autosaved sessions do not
   persist across restarts (browser localStorage and JSON export still work).
   This matches standalone behavior on the same tier.
5. **ElevenLabs widget** — the external AI coach script loads as before;
   it is unaffected but remains an external dependency.
6. **Two processes, one service** — `serve.py` runs both Streamlit
   apps plus an aiohttp proxy in one service. On Render's free tier
   (512 MB), two Python processes is workable but tight; the hub process
   stays light because it never imports the modeler. A crashed upstream
   surfaces as a brief 502 while it restarts.
7. **FM identity is its own** — the standalone modeler keeps its original
   branding (Operating Model, dark theme) by design; hub rebranding does
   not and should not reach into it.
8. **FM internal page position** — the Financial Modeler's sidebar page
   selector returns to its Home screen when the module is unmounted and
   re-entered (Streamlit clears unmounted widget state). Entered model
   data is unaffected — it lives in named session keys and the autosave
   file — and this matches standalone FM behavior.
9. **Placeholder views** — Recent Clients, Saved Scenarios, and Advisor
   Notes are stub pages; workspace data management is out of Build 1 scope.
