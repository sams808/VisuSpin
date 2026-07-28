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


# ---------------------------------------------------------------------------
# Lesson-narrative components. Every VisuSpin lesson follows the same shape:
# a motivating question up front, concept explained in plain language before
# any equation/plot, a "predict before you look" moment at the pivotal
# comparison, a one-line key-takeaway once the point has landed, and a link
# to the next lesson. These helpers keep that shape (and its look) consistent
# across every page without repeating the same HTML in each one. Colors use
# translucent (rgba) fills with no hardcoded text color, so they read
# correctly in both Streamlit's light and dark themes.
# ---------------------------------------------------------------------------

def lesson_header(lesson_label: str, title: str, question: str) -> None:
    """Opens a lesson: eyebrow label, title, and the motivating question in
    a bordered callout -- posed before any physics, plot, or slider appears."""
    st.markdown(
        f'<div style="text-transform:uppercase;letter-spacing:0.08em;font-size:0.78rem;'
        f'opacity:0.65;font-weight:600;margin-bottom:0.15rem;">{lesson_label}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"## {title}")
    st.markdown(
        f'<div style="border-left:4px solid {ACCENT};background:rgba(91,70,229,0.08);'
        f'border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin:0.8rem 0 1.2rem 0;">'
        f'<strong>Question to keep in mind:</strong> {question}</div>',
        unsafe_allow_html=True,
    )


def key_takeaway(text: str) -> None:
    """A visually distinct, consistent callout for the one-sentence insight
    a section was building toward -- placed right after the plot/comparison
    that demonstrates it, while it's fresh."""
    st.markdown(
        f'<div style="background:rgba(240,168,60,0.14);border:1px solid rgba(240,168,60,0.4);'
        f'border-radius:8px;padding:0.7rem 1rem;margin:0.9rem 0;">'
        f'<strong>Key takeaway —</strong> {text}</div>',
        unsafe_allow_html=True,
    )


def term(word: str, definition: str) -> str:
    """Consistent inline first-use definition, e.g. term('T2*', 'the FID's
    observed decay time, faster than T2 because it also includes...'). Returns
    a plain-Markdown fragment (bold + italic) to embed inline in an f-string
    passed to a normal st.markdown() call -- deliberately NOT raw HTML: a
    version of this using <strong>/<span> tags rendered as literal escaped
    text when embedded in an st.markdown() call that lacked
    unsafe_allow_html=True (confirmed via a headless-browser screenshot of
    the rendered page), and chasing that flag across every call site in
    every lesson is more fragile than just not needing it."""
    return f"**{word}** *({definition})*"


def predict_then_reveal(prompt: str, reveal_label: str = "Check your prediction"):
    """Poses a question and returns a closed expander to render the answer
    in -- use as `with predict_then_reveal("..."): st.pyplot(fig)`. Asking
    the student to commit to a guess before seeing the plot is a much
    stronger learning moment than watching a slider move."""
    st.markdown(f"**Before you look — what do you expect?** {prompt}")
    return st.expander(reveal_label, expanded=False)


def lesson_link(number: str, title: str, description: str, page_path: str) -> None:
    """One row of the Home-page learning path: a lesson number, title, and
    one-line description, with a working page_link (falling back to a plain
    caption if the page registry lookup fails -- see next_lesson)."""
    st.markdown(f"**Lesson {number}: {title}** — {description}")
    try:
        st.page_link(page_path, label="Open", icon="➡️")
    except Exception:
        st.caption(f"Open: {page_path}")


def next_lesson(label: str, page_path: str) -> None:
    """st.page_link raises KeyError('url_pathname') when a page is exercised
    in isolation (e.g. streamlit.testing.v1.AppTest.from_file on a single
    page, with no sibling pages registered) -- confirmed harmless there via a
    real running multipage server + headless-browser screenshot, where the
    link renders and navigates correctly. Caught here so it can't ever break
    a real page render if the registry lookup fails for any other reason."""
    st.divider()
    try:
        st.page_link(page_path, label=f"Continue: {label}", icon="➡️")
    except Exception:
        st.caption(f"Continue: {label} ({page_path})")
