import streamlit as st
import replicate
import time
from httpx import ReadTimeout

st.title("☃️ Frosty")

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How can I help?"}]

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    # Call LLM
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            input = {
                "prompt": st.session_state.messages[-1]["content"],
                "top_k": 50,
                "top_p": 0.9,
                "max_tokens": 700,
                "min_tokens": 0,
                "temperature": 0.2,
                "system_prompt": "You are a helpful assistant.",
                "stop_sequences": "<|im_end|>",
                "presence_penalty": 1.15,
                "frequency_penalty": 0.2
            }

            try:
                response = ""
                events = replicate.stream(
                    "snowflake/snowflake-arctic-instruct",
                    input=input
                )

                for event in events:
                    if event is not None:
                        event_data = event.data
                        if event_data is not None:
                            response += event_data  # Accumulate the stream response

            except Exception as e:
                response = f"An error occurred: {e}"

            st.write(response)

    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
