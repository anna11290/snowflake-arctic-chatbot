import streamlit as st

conn = st.connection("snowflake")
df = conn.query("select current_warehouse()")
st.write(df)