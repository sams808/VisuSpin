"""Shared Streamlit page setup so every page looks/behaves consistently."""
from __future__ import annotations
import sys
import os
import base64

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

ACCENT = "#5b46e5"
ASSETS_DIR = os.path.join(_ROOT, "assets")


def render_logo(width: int = 320) -> None:
    """Embeds the logo as a base64 data-URI <img>, not inline <svg> markup --
    Streamlit's markdown-to-HTML pass was found (via a headless-browser
    screenshot check) to mangle raw inline SVG containing XML comments,
    leaking part of the source as literal text. A data URI sidesteps that
    entirely since the browser only ever sees an <img> tag."""
    path = os.path.join(ASSETS_DIR, "logo.svg")
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        st.markdown(
            f'<img src="data:image/svg+xml;base64,{b64}" width="{width}" style="max-width:100%;">',
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        st.title("VisuSpin")


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""<div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.2rem;">
        <span style="font-size:1.7rem;font-weight:700;">{title}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.caption(subtitle)
    st.divider()
