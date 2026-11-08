"""
Financial Modeler — standalone application entry point.

Serves the Financial Modeler experience at ``/fm`` on the shared
Render service (see ``serve.py``). Runs in its own Streamlit process with
the original dark theme (passed via CLI/env by ``serve.py``), so none of
the SBI Hub shell's light-theme CSS, sidebar, or branding applies here.

Page configuration mirrors the original standalone app
(upstream ``NSC-Rick/FinanceModeler``).
"""
import streamlit as st

st.set_page_config(
    page_title="Financial Modeler",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

from sbi_hub.modules.financial_modeler import app as financial_modeler_app

financial_modeler_app.render()
