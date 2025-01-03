import re
import json
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.feedback import FeedbackAgent
from streamlit_folium import folium_static, st_folium
from components.sidebar import clear_chat_history
import plotly.graph_objects as go
from folium import Map
from utils.constants import TIMEOUT_SECONDS
import plotly.io as pio
pio.templates.default = "plotly"

@st.dialog("Maximum number of messages reached!")
def clear_chat():
    st.write("The chat history will be cleared.")
    if st.button("🧹Clear Chat!"):
        clear_chat_history()
        st.rerun()


def is_json_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False

# @st.cache_data(show_spinner="Displaying Map", ttl=3600, experimental_allow_widgets=True)
@st.fragment
def safe_folium_display(folium_map, message_id):
    if isinstance(folium_map, Map):
        try:
            # _folium_map.fit_bounds(_folium_map.get_bounds())
            # folium_static(_folium_map, height=400)
            st_folium(folium_map, height=400, width=600, key=message_id, render=False, returned_objects=[])
        except Exception as e:
            st.error(f"Error displaying Folium map: {str(e)}")
            st.write("Map data (non-rendered):")
            st.json(
                {
                    k: v
                    for k, v in folium_map.__dict__.items()
                    if is_json_serializable(v)
                }
            )
    else:
        st.error(
            f"Expected a Folium Map object, but received a different type. Received object of type: {type(_folium_map)}"
        )

@st.fragment
@st.cache_data(show_spinner="Displaying Figure", ttl=3600)
def safe_fig_display(fig):
    if isinstance(fig, plt.Figure):
        try:
            st.pyplot(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying Matplotlib figure: {str(e)}")
            st.write("Figure data (non-rendered):")
    elif isinstance(fig, go.Figure):
        try:
            fig.update_layout(height=800, width=600)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying Plotly figure: {str(e)}")
            st.write("Figure data (non-rendered):")
    else:
        st.error(
            f"Expected a Matplotlib or Plotly Figure object, but received a different type. Received object of type: {type(fig)}"
        )

@st.fragment
@st.cache_data(show_spinner="Displaying Dataframe", ttl=3600)
def safe_dataframe_display(data):
    try:
        # Convert various input types to DataFrame
        if not isinstance(data, pd.DataFrame):
            if isinstance(data, (list, tuple)):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame.from_dict(data)
            elif isinstance(data, np.ndarray):
                df = pd.DataFrame(data)
            else:
                try:
                    df = pd.DataFrame([data])
                except:
                    st.error(f"Could not convert type {type(data)} to DataFrame")
                    return
        else:
            df = data

        # Display DataFrame
        st.dataframe(
            df.reset_index(drop=True),
            use_container_width=True,
            height=50,
            hide_index=df.index.name is None or df.index.name == 'index',
        )
    except Exception as e:
        st.error(f"Error processing/displaying data: {str(e)}")
        st.write("Raw data (non-rendered):")
        st.json(data if isinstance(data, dict) else {"data": str(data)})


def apply_color_codes(text):
    def color_replacer(match):
        color = match.group(1)
        return f'<span style="color: {color}">{color}</span>'

    # Replace color codes with HTML spans
    colored_text = re.sub(r"(#[0-9A-Fa-f]{6})", color_replacer, text)

    # Wrap the entire text in a paragraph tag to ensure inline HTML is rendered
    return colored_text

@st.fragment
@st.cache_data(show_spinner="Displaying Code", ttl=3600)
def display_code_output(_message, message_id, only_text=False):
    if "code_output" not in _message or only_text:
        return

    if not _message.get("eval_success", False):
        st.write("Evaluation failed.")
        return

    code_output = _message["code_output"]
    with st.expander("✅Code Evaluation Output:", expanded=False):
        st.write(code_output)


def display_fig_map_dataframe(code_output, message_id):
    if "plot" in code_output and code_output["plot"] is not None:
        safe_fig_display(code_output["plot"])
    if "map" in code_output and code_output["map"] is not None:
        safe_folium_display(code_output["map"], message_id)
    if "dataframe" in code_output and code_output["dataframe"] is not None:
        safe_dataframe_display(code_output["dataframe"])


def display_figure(fig):
    if isinstance(fig, go.Figure):
        st.plotly_chart(fig, use_container_width=True)
    elif isinstance(fig, plt.Figure):
        st.pyplot(fig, use_container_width=True)


def display_feedback_ui(fb_agent, message_id, col2, col3):
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
            placeholder="Comment",
            key=f"{message_id}_comment",
            on_change=fb_agent.on_feedback_change,
        )


def display_llm_response(fb_agent, uuid, message, i):
    # Display Code if final response is different from the initial LLM response
    only_text = message["only_text"]
    message_id = f"{uuid}_{i}"
    st.session_state.current_message_id = message_id
    if not only_text:
        with st.expander("👨‍💻Code", expanded=False):
            executable_pattern = r"```python\n(.*?)```"
            executable_code = re.findall(
                executable_pattern, message["main_response"], re.DOTALL
            )
            code_block = "```python\n" + executable_code[0] + "\n```"
            st.code(executable_code[0] , wrap_lines=False, line_numbers =True, language="python")

    col1, col2, col3 = st.columns([6, 2, 1])
    with col1:
        if "code_output" in message and not only_text:
            # Default empty eval_success to False
            if message.get("eval_success", False):
                display_code_output(message, message_id)
            else:
                error_message = message["error_message"]
                if "TimeoutError" in error_message:
                    st.warning(
                        f"⏰Code execution timed out. Current timeout is {TIMEOUT_SECONDS//60} minutes.",
                    )
                    return  # Skip displaying the final message
                with st.expander("❌ :red[Error Message]", expanded=False):
                    st.error(f"\n {error_message}")
                if not st.session_state.get("retry_code", False):
                    st.error(
                        "Please edit your prompt or toggle `🔘Allow Retry`.", icon="⚠"
                    )
                else:
                    st.error(
                        "Code execution Failed! Please try again with a different prompt.",
                        icon="⚠",
                    )
                return  # Skip displaying the final message
        else:
            if only_text and "main_response" in message:
                st.write(message["main_response"])
            else:
                if "error_message" in message:
                    st.error(
                        f"Call Failed! Error: {message['error_message']}", icon="⚠"
                    )
                else:
                    st.error(
                        "Call Failed! Please try again with a different LLM.", icon="⚠"
                    )


    if only_text or message["summary_response"] != message["main_response"]:
        if message["summary_response"] is None:
            return
        colored_response = apply_color_codes(message["summary_response"])
        if message["is_cancelled"]:
            with col1:
                st.info(message["summary_response"], icon="🚨")
        else:
            display_feedback_ui(fb_agent, message_id, col2, col3)
            if len(colored_response) <= 500:
                with col1:
                    st.markdown(colored_response, unsafe_allow_html=True)
            else:
                st.markdown(colored_response, unsafe_allow_html=True)
    if isinstance(message["code_output"], dict):
        display_fig_map_dataframe(message["code_output"], message_id)


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
