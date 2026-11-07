# SBI Hub — Small Business Intelligence Hub

*Better Insights. Better Decisions. Stronger Businesses.*

A modular Streamlit application for small-business advisors. Build 1 delivers
the application shell and integrates the existing **Financial Modeler**
(Operating Model) as the first operational module.

## Modules

| Module | Status |
|---|---|
| Financial Modeler | **Active** |
| Business Idea & Feasibility | Coming Soon |
| Business Valuation & Succession | Coming Soon |
| Workforce & Hiring | Coming Soon |
| Capital Investment | Coming Soon |
| Sales & Growth | Coming Soon |
| Operations Modeler | Coming Soon |
| Automation & AI Opportunity Evaluator | Coming Soon |

## Architecture

Modular monolith, single web service:

```
app.py                        # Entry point: page config + module router
sbi_hub/
├── shell/                    # Application shell
│   ├── landing.py            # Landing page (hero, cards, announcements panel)
│   ├── announcements.py      # Announcements loader + renderer
│   └── theme.py              # Vermont navy/teal/green CSS
├── config/
│   ├── modules.py            # Module registry (id, name, status)
│   └── announcements.json    # Announcements config file
└── modules/
    └── financial_modeler/    # Vendored Financial Modeler (see below)
        ├── app.py            # render() entry called by the hub router
        ├── engine/           # Pure calculation engine (unchanged)
        ├── ui/               # Modeler screens (unchanged)
        ├── utils/            # Session, export, styles (unchanged)
        ├── analysis/  components/  config/  docs/  tests/
tests/                        # Hub-level + integration tests
.streamlit/config.toml        # Dark Vermont theme
render.yaml                   # Render service definition
```

## Financial Modeler integration

The Financial Modeler source (upstream `NSC-Rick/FinanceModeler` @ `49f2a0c`,
platform v0.9.3) is vendored under `sbi_hub/modules/financial_modeler/`.
The production repository, Render service, and user data are untouched.

Changes made during vendoring — none alter modeling logic:

- Imports rewritten from top-level (`from engine ...`) to package-qualified
  (`from sbi_hub.modules.financial_modeler.engine ...`).
- `app.py` wrapped in `render()`; `st.set_page_config` moved to the hub
  shell (it may only be called once per app).
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
streamlit run app.py
```

## Deployment (Render)

`render.yaml` defines a free-tier Python web service:

- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Testing

```bash
pytest
```

## Build 1 Validation Report

- **234 tests passing** (209 vendored Financial Modeler baseline tests +
  25 new hub tests) covering engine calculations, P&L/cash-flow statements,
  loan amortization, capital stack, scenario JSON save/load validation,
  Excel export, module registry integrity, announcement ordering, and
  app-level navigation (landing → Financial Modeler → back to hub) via
  Streamlit `AppTest`.
- App boots clean: `streamlit run app.py` serves the landing page with all
  eight module cards; the Financial Modeler renders and returns to the hub.
- Synthetic data only; no real client data stored or migrated.

### Known limitations / risks

1. **Vendored code drift** — upstream Financial Modeler fixes must be
   re-vendored into `sbi_hub/modules/financial_modeler/` manually.
2. **Shared session state** — hub and module share `st.session_state`.
   Keys are namespaced by convention (`nav`, `active_view` for the hub);
   future modules should use a `{module_id}__` prefix to avoid collisions.
3. **Single `set_page_config`** — the hub owns page config; module-level
   titles/icons now show "SBI Hub" in the browser tab.
4. **Session file scope** — `~/.finlite_session.json` is per-server-home;
   on ephemeral Render free-tier filesystems, autosaved sessions do not
   persist across restarts (browser localStorage and JSON export still work).
   This matches standalone behavior on the same tier.
5. **ElevenLabs widget** — the external AI coach script loads as before;
   it is unaffected but remains an external dependency.
6. **Theme** — the hub theme (dark navy/teal) applies globally; the
   Financial Modeler keeps its dark styling unchanged.
