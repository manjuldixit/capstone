import json
from pathlib import Path
from typing import Dict, Optional

import requests
import streamlit as st

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"
SCENARIO_FILE = Path(__file__).resolve().parents[1] / "backend" / "mockdata" / "phase9_evaluation_scenarios.json"


def init_page() -> None:
    st.set_page_config(
        page_title="AI Advisory Agent Equipment Financing",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("AI Advisory Agent Equipment Financing")
    st.markdown(
        "Interact with the Phase 8/9 deployment-ready agent, collect feedback, and inspect adaptive behavior in real time."
    )


def get_session_state() -> Dict[str, Optional[str]]:
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "last_response" not in st.session_state:
        st.session_state.last_response = None
    return {
        "session_id": st.session_state.session_id,
        "conversation": st.session_state.conversation,
        "last_response": st.session_state.last_response,
    }


def call_backend(endpoint: str, payload: Dict[str, str], backend_url: str) -> Dict:
    url = backend_url.rstrip("/") + endpoint
    try:
        response = requests.post(url, json=payload, timeout=25)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        st.error(f"Backend HTTP error: {exc.response.status_code if exc.response is not None else 'unknown'} - {message}")
        raise
    except requests.RequestException as exc:
        st.error(f"Backend error: {exc}")
        raise


def fetch_health(backend_url: str) -> Dict:
    try:
        response = requests.get(f"{backend_url.rstrip('/')}/health", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"status": "unhealthy", "ready": False}


def fetch_adaptation(backend_url: str, session_id: Optional[str]) -> Dict:
    try:
        url = f"{backend_url.rstrip('/')}/adaptation"
        if session_id:
            url = f"{url}?session_id={session_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc)}


def append_message(role: str, content: str, metadata: Dict = None) -> None:
    st.session_state.conversation.append({
        "role": role,
        "content": content,
        "metadata": metadata or {}
    })
    st.session_state.last_response = content


def render_conversation() -> None:
    for message in st.session_state.conversation:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            metadata = message.get("metadata", {})
            with st.container():
                st.markdown(f"**Agent:** {message['content']}")
                if metadata:
                    st.caption(
                        f"Phase: {metadata.get('phase', 'N/A')} | Confidence: {metadata.get('confidence', 'N/A')} | "
                        f"Adaptive: {metadata.get('adaptive_applied', False)}"
                    )
        st.markdown("---")


def load_scenarios() -> list:
    if not SCENARIO_FILE.exists():
        return []
    try:
        with SCENARIO_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def submit_query(query: str, backend_url: str) -> None:
    payload = {
        "query": query,
        "session_id": st.session_state.session_id
    }
    response = call_backend("/query", payload, backend_url)
    session_id = response.get("session_id")
    if session_id:
        st.session_state.session_id = session_id
    result = response.get("result", {})
    metadata = {
        "phase": result.get("phase"),
        "confidence": result.get("confidence"),
        "adaptive_applied": result.get("adaptive_applied", False),
        "adaptive_action": result.get("adaptive_action")
    }
    append_message("user", query)
    append_message("agent", result.get("response", "No response returned."), metadata)


def submit_feedback(rating: int, comments: str, backend_url: str) -> None:
    if not st.session_state.conversation or not st.session_state.last_response:
        st.warning("Please ask a query before submitting feedback.")
        return

    last_user = next((m for m in reversed(st.session_state.conversation) if m["role"] == "user"), None)
    if not last_user:
        st.warning("No user query available for feedback.")
        return

    feedback_payload = {
        "query": last_user["content"],
        "response": st.session_state.last_response,
        "rating": rating,
        "comments": comments,
        "session_id": st.session_state.session_id
    }
    response = call_backend("/feedback", feedback_payload, backend_url)
    if response.get("feedback"):
        st.success("Feedback submitted successfully.")
    else:
        st.error("Unable to store feedback. Check backend logs.")


def main() -> None:
    init_page()
    state = get_session_state()

    with st.sidebar:
        st.header("Session Control")
        backend_url = st.text_input("Backend URL", DEFAULT_BACKEND_URL)
        if st.button("Check backend health"):
            health = fetch_health(backend_url)
            st.write(health)

        if st.button("Refresh adaptation summary"):
            adaptation = fetch_adaptation(backend_url, state["session_id"])
            st.write(adaptation)

        if st.button("Reset session"):
            st.session_state.session_id = None
            st.session_state.conversation = []
            st.session_state.last_response = None
            st.experimental_rerun()

        st.markdown("---")
        st.markdown("### Session ID")
        st.code(state["session_id"] or "Not established yet")

        st.markdown("---")
        st.markdown("### Sample evaluation scenarios")
        scenarios = load_scenarios()
        for scenario in scenarios[:5]:
            st.write(f"- {scenario.get('query_text')}")

    st.subheader("Ask the ai-banking-advisory-agent Agent")
    with st.form(key="query_form"):
        query_text = st.text_area("Your question", height=120)
        submit_button = st.form_submit_button("Submit query")
    if submit_button and query_text.strip():
        submit_query(query_text.strip(), backend_url)

    if st.session_state.conversation:
        st.subheader("Conversation")
        render_conversation()

    with st.expander("Submit feedback for the latest agent response"):
        rating = st.slider("Rating", min_value=1, max_value=5, value=4)
        comments = st.text_area("Comments", help="What did you like or what should improve?")
        if st.button("Send feedback"):
            submit_feedback(rating, comments, backend_url)

    st.markdown("---")
    st.subheader("How to use")
    st.markdown(
        "1. Start the backend API with `python deploy_server.py` from `capstone/ai-banking-advisory-agent/backend`.\n"
        "2. Run this frontend with `streamlit run frontend/app.py`.\n"
        "3. Enter a query, inspect the agent response, then optionally provide feedback to drive adaptive behavior."
    )


if __name__ == "__main__":
    main()

