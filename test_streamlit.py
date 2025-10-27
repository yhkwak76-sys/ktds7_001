import streamlit as st
import pandas as pd

st.title("Streamlit Data Display Example")
st.write("Welcome to Streamlit") 

df =pd.DataFrame({
    'Column A': [1, 2, 3, 4],
    'Column B': ['A', 'B', 'C', 'D']
})

st.write(df)

# python -m streamlit run D:\EDU\ktds7_001\test_streamlit.py
# streamlit run .\07.streamlit_data.py