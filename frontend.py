# pylint: disable=unused-variable
# pylint: disable=anomalous-backslash-in-string

import generic
import pandas as pd
import numpy as np
import math
import altair as alt
import pydeck as pdk
import streamlit as st

read_columns = {7:['confirmed','State-level Cumulative'],9:['i_confirmed','State-level Changes'],11:['Tot_confirmed','Country-level Cumulative'],12:['iTot_confirmed','Country-level Changes'],15:['deaths','State-level Cumulative'],17:['i_deaths','State-level Changes'],19:['Tot_deaths','Country-level Cumulative'],20:['iTot_deaths','Country-level Changes']}

# Module to display sidebar
def display_sidebar(data):
    # adm0_a3, Country/Region
    sel_region,sel_country = None, None

    # Sidebar sections to provide choices (Region, State)
    # if not check:
    #     # Choose a startdate to display
    #     st.sidebar.header('Choose a startdate below')
    #     st.sidebar.markdown('Choose a startdate (e.g., 2020-08-15)')
    #     startdate = st.sidebar.slider('Startdate',data['Date'].unique()[0],data['Date'].unique()[-1])
    #
    # else:

    st.header('Choose options below')
    # 0) Need to reset data
    if st.button(label='Reset'):
        st.caching.clear_cache()
        st.experimental_rerun()
    
    # 1) Choose a Region/Country to display
    # st.sidebar.subheader('Choose Region/Country below')
    # st.sidebar.subheader('*Note*: Only multi-states countries are currently supported!')

    # Set candiates of region (Country/Region)
    # st.sidebar.header('Choose Region/Country/State below')
    # st.markdown('Choose a Country/Region (e.g., Canada)')
    country = sorted(data.loc[data['len_states']>1,'Country/Region'].unique())
    country = ['India']
    sel_country = 'India'

    # Candiates of countries (adm0_a3) are automatically set
    if sel_country and sel_country != 'Worldwide':
        sel_region = data.loc[(data['len_states']>1) &  (data['Country/Region'].str.contains(sel_country)),'adm0_a3'].unique()[0]

    # 2) Choose a statistics
    # st.text([val[1] for val in read_columns.values()])
    st.markdown('Choose a Statistics (e.g., State-level Changes)')
    if sel_region:
        stat_text = sorted(list(set(val[1] for val in read_columns.values() if val[1][0]=='S')))
    else:
        stat_text = sorted(list(set(val[1] for val in read_columns.values() if val[1][0]=='C')))
    stat_text = [None] + stat_text[:]
    chosen_stat_text = st.selectbox('Statistics',stat_text)

    if chosen_stat_text:
        chosen_stat_key = [val[0] for val in read_columns.values() if val[1] in chosen_stat_text]
    else:
        chosen_stat_key = None

    chosen_stat = {}
    if chosen_stat_text:
        for key in chosen_stat_key:
            chosen_stat[key] = chosen_stat_text

    # 3) Draw map
    # st.markdown('Draw a map?')
    # sel_map = st.checkbox('Definitely')

    return sel_region, sel_country, chosen_stat, True

# Print latest global status
def show_stats(data,sel_region,sel_country,chosen_stat,candidates,map=None):
    date = max(data['Date'])
    st.header('Summary statistics')

    if not sel_region:
        st.subheader('Global status as of ' + date.strftime('%m/%d/%y'))
        st.markdown(f"Cumulative infections:  `{data[data['Date']==date].groupby(['adm0_a3','Country/Region'])['Tot_confirmed'].max().sum():,}`")
        st.markdown(f"Cumulative casualties: `{data[data['Date']==date].groupby(['adm0_a3','Country/Region'])['Tot_deaths'].max().sum():,}`")
        st.markdown(f"Daily infections changes: `{data[data['Date']==date].groupby(['adm0_a3','Country/Region'])['iTot_confirmed'].max().sum():,}`")
        st.markdown(f"Daily casualties changes: `{data[data['Date']==date].groupby(['adm0_a3','Country/Region'])['iTot_deaths'].max().sum():,}`")

    else:
        st.subheader(sel_country + ' status as of ' + date.strftime('%m/%d/%y'))
        st.markdown(f"Cumulative infections:  `{data[(data['Date']==date) & (data['adm0_a3']==sel_region) & (data['Country/Region']==sel_country)].groupby(['adm0_a3','Country/Region'])['Tot_confirmed'].max().sum():,}`")
        st.markdown(f"Cumulative casualties: `{data[(data['Date']==date) & (data['adm0_a3']==sel_region) & (data['Country/Region']==sel_country)].groupby(['adm0_a3','Country/Region'])['Tot_deaths'].max().sum():,}`")
        st.markdown(f"Daily infections changes: `{data[(data['Date']==date) & (data['adm0_a3']==sel_region) & (data['Country/Region']==sel_country)].groupby(['adm0_a3','Country/Region'])['iTot_confirmed'].max().sum():,}`")
        st.markdown(f"Daily casualties changes: `{data[(data['Date']==date) & (data['adm0_a3']==sel_region) & (data['Country/Region']==sel_country)].groupby(['adm0_a3','Country/Region'])['iTot_deaths'].max().sum():,}`")

    show_chart(data,chosen_stat,candidates,sel_region)

    if map and chosen_stat:
        show_map(data,chosen_stat,sel_region)

# Load mapdata for selected region
def show_map(data,stat,region=None,date=None):
    st.subheader('Color maps')
    st.write('Color depths: Infections')
    st.write('Elevation: Casualties')
    if not date:
        date = max(data['Date'])

    # Load in the JSON data
    if region and region != 'Worldwide':
        src_geo = 'states_india.json'
    else:
        src_geo = 'states_india.json'

    json_geo = pd.read_json(src_geo)
    df = pd.DataFrame()

    # Custom color scale (colorbrewer2.org -> Sequential Single-Hue)
    breaks = [.0, .2, .4, .6, .8, 1]
    color_range = [
        # 6-class Blues
        [255,255,255],
        [198,219,239],
        [158,202,225],
        [107,174,214],
        [49,130,189],
        [8,81,156],

        # # 6-class Purples (For reference)
        # [242,240,247],
        # [218,218,235],
        # [188,189,220],
        # [158,154,200],
        # [117,107,177],
        # [84,39,143],
    ]

    def color_scale(val):
        for i, b in enumerate(breaks):
            if val <= b:
                return color_range[i]
        return color_range[i]

    def elevation_scale(val,scale):
        for i, b in enumerate(breaks):
            if val <= b:
                return i*scale


    def set_nan(val):
        if np.isnan(val):
            return -1
        else:
            return val


    # Parse the geometry out in Pandas
    df["coordinates"] = json_geo["features"].apply(lambda row: row["geometry"]["coordinates"])
    df["name"] = json_geo["features"].apply(lambda row: row["properties"]["name"])
    df["adm0_a3"] = json_geo["features"].apply(lambda row: row["properties"]["adm0_a3"])
    df["admin"] = json_geo["features"].apply(lambda row: row["properties"]["admin"])

    stat_text = list(stat.values())[0]
    stat_keys = list(stat.keys())

    data = data.loc[data['Date']==date,['adm0_a3','Province/State','lat','lon',stat_keys[0],stat_keys[1]]]

    if not region or region == 'Worldwide':
        data = data.groupby(['adm0_a3'])[['lat','lon',stat_keys[0],stat_keys[1]]].mean()
        df = pd.merge(df,data,how='inner',left_on=['adm0_a3'],right_on=['adm0_a3'])
        zoom = 1
    else:
        data = data.loc[data['adm0_a3']==region,['adm0_a3','Province/State','lat','lon',stat_keys[0],stat_keys[1]]]
        df = pd.merge(df,data,how='inner',left_on=['name','adm0_a3'],right_on=['Province/State','adm0_a3'])
        zoom = 3

    # Moved to generic.py
    # df.loc[df[stat_keys[0]]<0,stat_keys[0]] = 0
    # df.loc[df[stat_keys[1]]<0,stat_keys[1]] = 0
    # df[stat_keys[0]] = df[stat_keys[0]].apply(set_nan)
    # df[stat_keys[1]] = df[stat_keys[1]].apply(set_nan)


    df['fill_color'] = (df[stat_keys[0]]/df[stat_keys[0]].max()).replace(np.nan,0).apply(color_scale)
    df['elevation'] = (df[stat_keys[1]]/df[stat_keys[1]].max()).replace(np.nan,0).apply(lambda x:elevation_scale(x,1e4))

    df['param'] = stat_text
    df.rename(columns={stat_keys[0]:'stat_0',stat_keys[1]:'stat_1'},inplace=True)

    # st.write(df)

    view_state = pdk.ViewState(
        latitude = df.loc[(df['lat'] != 0) & (df['lon'] != 0),'lat'].mean(skipna=True),
        longitude = df.loc[(df['lat'] != 0) & (df['lon'] != 0),'lon'].mean(skipna=True),
        # bearings=15,
        # pitch=45,
        zoom=zoom)

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        df,
        id="geojson",
        opacity=0.2,
        stroked=False,
        get_polygon="coordinates",
        filled=True,
        get_elevation='elevation',
        # elevation_scale=1e5,
        # elevation_range=[0,100],
        extruded=True,
        # wireframe=True,
        get_fill_color= 'fill_color',
        get_line_color=[255, 255, 255],
        auto_highlight=True,
        pickable=True,
    )

    # scatter_layer = pdk.Layer(
    #     "ScatterplotLayer",
    #     df,
    #     opacity=0.8,
    #     stroked=False,
    #     get_position=["lon","lat"],
    #     radius_scale = 10,
    #     radius_min_pixels = 0,
    #     radius_max_pixels= 50,
    #     get_radius='stat_1',
    #     filled=True,
    #     # extruded=True,
    #     # wireframe=True,
    #     # get_fill_color=[180, 0, 200, 140],
    #     get_line_color=[255, 0, 0],
    #     auto_highlight=True,
    #     pickable=True,
    # )

    tooltip = {"html": "<b>Country/Region:</b> {admin} <br /><b>Province/State:</b> {name} <br /><b>Type:</b> {param}<br /><b>Infections:</b> {stat_0} <br /><b>Casualties:</b> {stat_1}"}


    r = pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style='light',
        tooltip=tooltip,
        )

    # return r
    st.pydeck_chart(r, use_container_width=True)


def show_chart(data,stat,candidates,region,date=None):
    if not date:
        date = min(data['Date'])

    # Set quantiles for x-axis ('Date')
    dates = data['Date'].map(lambda x:x.strftime('%m/%d/%y')).unique().tolist()
    presets = [0,.25,.5,.75,1]
    quantiles = np.quantile(np.arange(0,len(dates)),presets).tolist()
    quantiles = [int(np.floor(q)) for q in quantiles]
    date_visible = [dates[idx] for idx in quantiles]

    if stat:
        st.header('Regional analyses')
        stat_text = ['Infections','Casualties']
        stat_keys = list(stat.keys())

        data = data.loc[(data['Date']>=date),['Date','adm0_a3','Country/Region','Province/State',stat_keys[0],stat_keys[1]]]

        for idx, stat_key in enumerate(stat_keys):
            if region:
                filtered_data = pd.merge(data[['Date','Province/State',stat_key]],candidates[['index',stat_key]],how='inner',left_on='Province/State',right_on=stat_key)
                filtered_data.drop([stat_key+'_y'],axis=1,inplace=True)
                filtered_data.rename(columns={stat_key+'_x':stat_key,'index':'order'},inplace=True)

                filtered_data['Date'] = filtered_data['Date'].map(lambda x:x.strftime('%m/%d/%y'))

                target_cat = 'Province/State'
            else:
                filtered_data = pd.merge(data[['Date','adm0_a3','Country/Region',stat_key]],candidates[['index',stat_key]],how='inner',left_on='adm0_a3',right_on=stat_key)
                filtered_data.drop([stat_key+'_y'],axis=1,inplace=True)
                filtered_data.rename(columns={stat_key+'_x':stat_key,'index':'order'},inplace=True)

                filtered_data['Date'] = filtered_data['Date'].map(lambda x:x.strftime('%m/%d/%y'))

                target_cat = 'Country/Region'
            if idx == 0:
                st.subheader('Infections developments')
            else:
                st.subheader('Casualties developments')

            heatmap = alt.Chart(filtered_data).mark_rect().encode(
                x=alt.X('Date:O', sort=dates, axis=alt.Axis(values=date_visible,labelAngle=0)),
                y=alt.Y(target_cat, sort=alt.EncodingSortField(field='order',order='ascending')),
                color=alt.Color(stat_key,scale=alt.Scale(scheme='blues'),title=stat_text[idx]),
                tooltip=['Date:O',target_cat,alt.Tooltip(stat_key,title=stat_text[idx],format=',')]
                ).configure_scale(
                    bandPaddingInner=.1
                    )

            st.altair_chart(heatmap,use_container_width=True)
