import streamlit as st
import replicate
import re
import time
from prompts import get_system_prompt

st.title("☃️ Frosty")

# Initialize the chat messages history
if "messages" not in st.session_state:
    # System prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# Prompt for user input and save
if prompt := st.chat_input("Your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])

# If the last message is not from the assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            input = {
                "prompt": st.session_state.messages[-1]["content"],
                "top_k": 50,
                "top_p": 0.9,
                "max_tokens": 512,
                "min_tokens": 0,
                "temperature": 0.2,
                "system_prompt": get_system_prompt(),
                "stop_sequences": "",
                "presence_penalty": 1.15,
                "frequency_penalty": 0.2
            }

            try:
                response = ""
                events = replicate.stream(
                    "snowflake/snowflake-arctic-instruct",
                    input=input
                )

                response_container = st.empty()  # Container to update the response in real-time

                for event in events:
                    if event is not None:
                        event_data = event.data
                        if event_data is not None:
                            response += event_data  # Accumulate the stream response
                            response_container.markdown(response)  # Update the container with the current response

                # Update the final response after streaming completes
                response_container.markdown(response)
                message = {"role": "assistant", "content": response}

                # Parse the response for a SQL query and enforce LIMIT 10
                sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
                if sql_match:
                    sql = sql_match.group(1)
                    # Ensure LIMIT 10 is present in the SQL query
                    if not re.search(r"\bLIMIT\b\s+\d+", sql, re.IGNORECASE):
                        sql = re.sub(r";\s*$", "", sql)  # Remove trailing semicolon if present
                        sql += " LIMIT 10"  # Append LIMIT 10

                    conn = st.connection("snowflake")
                    message["results"] = conn.query(sql)
                    st.dataframe(message["results"])

                st.session_state.messages.append(message)
            except Exception as e:
                st.error(f"An error occurred: {e}")
