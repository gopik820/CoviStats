import streamlit as st
from PIL import Image
import webbrowser

def app():
    left_column_1, center_column_1, right_column_1 = st.beta_columns(3)
    with left_column_1:
        img = Image.open("images/arungovindm2001.jpeg")
        st.image(img, width=200)
        st.write("Arun Govind M")
        st.write("Member of amFOSS")
        if(st.button("GitHub:arungovindm2001")):
            webbrowser.open(
                'https://github.com/arungovindm2001')

    with center_column_1:
        img = Image.open("images/gopik820.jpeg")
        st.image(img, width=200)    
        st.write("Gopikrishna K")
        st.write("Member of amFOSS")
        if(st.button("GitHub:gopik820")):
            webbrowser.open(
                'https://github.com/gopik820')

    with right_column_1:
        img = Image.open("images/siddharthc30.jpeg")
        st.image(img, width=200)
        st.write("Siddharth C")
        st.write("Member of amFOSS")
        if(st.button("GitHub:siddharthc30")):
            webbrowser.open(
                'https://github.com/siddharthc30')