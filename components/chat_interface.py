import folium
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from utils.feedback import FeedbackAgent
from streamlit_folium import folium_static
from components.sidebar import clear_chat_history
import plotly.graph_objects as go

@st.dialog("Maximum number of messages reached!")
def clear_chat():
    st.write("The chat history will be cleared.")
    if st.button("OK"):
        clear_chat_history()
        st.rerun()

def display_code_output(message, only_text=False):
    if "code_output" not in message or only_text:
        return

    code_output = message["code_output"]
    st.write("Code Evaluation Result:")

    if not message.get("eval_success", False):
        st.write("Evaluation failed.")
        return

    display_functions = {
        plt.Figure: lambda x: st.pyplot(x, use_container_width=False),
        go.Figure: lambda x: st.plotly_chart(x, use_container_width=False),
        folium.Map: folium_static,
        pd.Series: lambda x: st.write(x.to_dict()),
    }

    if isinstance(code_output, dict):
        if "map" in code_output:
            folium_static(code_output["map"])
        for key in ["plot", "figure"]:
            if key in code_output:
                display_figure(code_output[key])
    elif isinstance(code_output, tuple(display_functions.keys())):
        display_functions[type(code_output)](code_output)
    else:
        st.write(code_output)

def display_figure(fig):
    if isinstance(fig, go.Figure):
        st.plotly_chart(fig, use_container_width=False)
    elif isinstance(fig, plt.Figure):
        st.pyplot(fig, use_container_width=False)

def display_llm_response(fb_agent, uuid, message, i):
    # Display Code if final response is different from the initial LLM response
    only_text = message["only_text"]
    if not only_text:
        with st.expander("👨‍💻Code", expanded=False):
            # with st.expander("LLM Response", expanded=False):
            st.write(message["code_response"])

    col1, col2, col3 = st.columns([6, 2, 1])

    with col1:
        if "code_output" in message and only_text is False:
            if message.get("eval_success", False):  # Default to False
                display_code_output(message)
            else:
                with st.expander("❌ :red[Code evaluation failed]", expanded=False):
                    st.error(f"\n {message['error_message']}")
                st.warning(
                    "Something went wrong with running the code. Please edit your prompt or toggle `🔘Allow Retry`.",
                    icon="⚠",
                )

    message_id = f"{uuid}_{i}"
    st.session_state.current_message_id = message_id

    with col3:
        st.feedback(
            key=f"{message_id}_feedback",
            on_change=fb_agent.on_feedback_change,
            options="thumbs",
        )
    with col2:
        st.text_input(
            "Comment:",
            label_visibility="collapsed",
            placeholder="Comment (optional):",
            key=f"{message_id}_comment",
            on_change=fb_agent.on_feedback_change,
        )

    if only_text or message["final_response"] != message["code_response"]:
        st.write(message["final_response"])


def display_chat_history(fb_agent: FeedbackAgent, uuid: str):
    for index, message in enumerate(st.session_state.chat_history):
        avatar = "🚍" if message["role"] == "assistant" else "🙋‍♂️"
        with st.chat_message(message["role"], avatar=avatar):
            ## Display user message
            if message["role"] == "user":
                st.write(message["content"])
            ## Display assistant message
            else:
                display_llm_response(fb_agent, uuid, message, index)
