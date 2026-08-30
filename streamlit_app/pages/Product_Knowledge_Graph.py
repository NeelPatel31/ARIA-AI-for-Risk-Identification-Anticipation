from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Product Knowledge Graph", layout="wide")

_html = (
    Path(__file__).resolve().parent.parent
    / "visualization"
    / "product-supply-chain-knowledge-graph.html"
).read_text(encoding="utf-8", errors="replace")

components.html(_html, height=900, scrolling=True)