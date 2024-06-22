import streamlit as st

options = st.multiselect(
    "What are your favorite colors",
    ["Green", "Yellow", "Red", "Blue", "Valeria", "Mario", "Elena"],
    ["Valeria", "Mario", "Elena"])


st.write("You selected:", options)


txt = st.text_area(
    "Text to analyze",
    "Please explain here which kind of vacation you wish to have",
    )

st.write(txt*500)

options_selectbox = tuple(options)

option = st.sidebar.selectbox(
    "How would you like to be contacted?",
    options_selectbox)

st.sidebar.write("You selected:", type(option))
