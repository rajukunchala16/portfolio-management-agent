"""Streamlit frontend for the portfolio management agent."""

import os

import requests
import streamlit as st


def get_backend_url() -> str:
    """Return the backend URL from environment or default local development value."""
    return os.getenv("PORTFOLIO_AGENT_API_URL", "http://localhost:8000").rstrip("/")


backend_url = get_backend_url()

st.set_page_config(page_title="Portfolio Management Agent", page_icon="📈", layout="wide")
st.title("Portfolio Management Agent")
st.caption("Ask your portfolio questions in natural language.")

question = st.text_area(
    "Your question",
    placeholder="e.g. What is my portfolio performance today?",
    height=120,
)

if st.button("Ask Agent", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{backend_url}/ask",
                    json={"question": question},
                    timeout=120,
                )

            if response.status_code == 200:
                payload = response.json()
                st.success("Response received")
                st.markdown("### Answer")
                st.write(payload.get("answer", "No answer returned."))
            else:
                try:
                    detail = response.json()
                    error_message = detail.get("detail", response.text)
                except ValueError:
                    error_message = response.text
                st.error(f"Request failed: {error_message}")
        except requests.RequestException as exc:
            st.error(
                "Could not reach the backend. "
                f"Check that the FastAPI service is running at {backend_url}. "
                f"Error: {exc}"
            )

st.markdown("---")
# st.caption(f"Backend URL: {backend_url}")
