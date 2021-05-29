import app1
import app2
import streamlit as st

PAGES = {
    "Dashboard": app2,
    "Vaccination Slots": app1
}
st.set_page_config(layout='wide',
                   initial_sidebar_state='expanded',
                   page_icon="https://www.cowin.gov.in/favicon.ico",
                   page_title="Covid Dashboard")
st.sidebar.title('Navigation')
selection = st.sidebar.selectbox("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()
