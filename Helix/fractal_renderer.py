# --- Replace your top canvas block with this ---
import streamlit as st
from fractal_renderer import FractalRenderer

if 'top_renderer' not in st.session_state:
    st.session_state.top_renderer = FractalRenderer(defaults={
        "zoom": 1.0228,
        "harmony": 0.5,
        "resilience": 1.0,
        "prana": 0.5,
        "drishti": 0.5
    })

st.subheader("ψ-Field Resonance Visualizer (Top Layer)")
renderer = st.session_state.top_renderer

try:
    psi_field.field = psi_field.field  # ensure it exists
    renderer.update(psi_field)
    renderer.draw(st)
except Exception as e:
    st.warning(f"⚠️ Renderer inactive or missing field: {e}")
    renderer.render_field()            st.pyplot(fig)
