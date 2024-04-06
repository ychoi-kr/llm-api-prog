import streamlit as st

st.title("비밀")

if st.button("말해"):
    st.write(st.secrets["MY_SECRET"])

