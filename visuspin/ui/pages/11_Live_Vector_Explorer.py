import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from common import page_header

st.set_page_config(page_title="VisuSpin — Live Vector Explorer", page_icon="🧲", layout="wide")
page_header(
    "Live Vector Explorer",
    "A real-time, 60fps companion to Lesson 1 — the same Bloch-equation physics, but animated live "
    "instead of recomputed per click. Also runs standalone: double-click run_visuspin_live.bat.",
)

_VISUSPIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HTML_PATH = os.path.join(_VISUSPIN_DIR, "classic", "live_vector_explorer.html")

if os.path.exists(_HTML_PATH):
    st.iframe(_HTML_PATH, height=1500)
else:
    st.error(f"Could not find the live explorer at {_HTML_PATH}.")
