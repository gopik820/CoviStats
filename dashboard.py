# pylint: disable=unused-variable
# pylint: disable=anomalous-backslash-in-string

'''
app.py: Frontend runner file for nCovid_19 Streamlit application

Dependencies
data: data/time_series_covid19.csv
modules:
frontend.py: Front-end works
generic.py: Load necessary files (infections, map)
'''

import streamlit as st
import pandas as pd
import generic
import frontend
import pydeck as pdk
import math

def app():

    filename = 'https://github.com/staedi/nCOV-summary/raw/master/time_series_covid19_infections.csv'

    ################################################################
    # Header and preprocessing

    # Set Title
    st.title('CoviStats')
    st.header('Covid 19 India Status Dashboard')

    # Initial data load
    update_status = st.markdown("Loading infections data...")
    covid = generic.read_dataset(filename)
    update_status.markdown('Load complete!')

    ################################################################
    # Sidebar section (Only multi-states country can be chosen)
    sel_region, sel_country, chosen_stat, sel_map = frontend.display_sidebar(covid)


    ################################################################
    # Main section
    update_status.markdown("Finding top districts...")
    cand = generic.set_candidates(covid, sel_region, sel_country, chosen_stat)
    update_status.markdown("Calculation complete!")

    update_status.markdown("Drawing charts")
    if sel_map:
        update_status.markdown("Drawing charts & maps...")
    else:
        update_status.markdown("Drawing charts...")
    frontend.show_stats(covid, sel_region, sel_country, chosen_stat, cand, sel_map)
    update_status.markdown("Job Complete!")
