#!/usr/bin/env python
# coding: utf-8
# Importing full packages
# import geopy
# import openpyxl
import streamlit as st
# import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import leafmap.foliumap as leafmap
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
# import pyodbc

# Importing partial packagesfrom geopy.exc import GeocoderTimedOut
# from geopy.geocoders import Nominatim

# Read in Data
activity_fin = pd.read_excel('FINAL Guinea TIPAC Hackathon Data Set.xlsx', 
             sheet_name = 'Financing of Activities')
activity_fin = activity_fin.rename(columns={'Amount of Finance Recevied': 'Amount of Finance Received'})
activity_fin.head()

# Create Figures
# Pie Chart
# https://plotly.com/python/pie-charts/

# graph activity vs. amount of finance received
activ_fin_df = pd.DataFrame(activity_fin.groupby(by = ['Name of Activity'], as_index = False)['Amount of Finance Received'].sum())
activ_fin_fig = px.histogram(activ_fin_df, x= "Name of Activity", y = "Amount of Finance Received",
             barmode='group').update_xaxes (categoryorder="total ascending")

# plot pie chart for same data
activ_pie = px.pie(activ_fin_df, values='Amount of Finance Received', names='Name of Activity')

# 100 percent stacked bar chart
activ_stack_df = pd.DataFrame(activity_fin.groupby(by = ['Name of Activity'],
                                                 as_index = False)[['Amount of Finance Received',
                                                                   'Cost of Subactivity in GNF',
                                                                   'Gap']].sum())
activ_stack_mlt = pd.melt(activ_stack_df, id_vars = 'Name of Activity')

# st.subheader('Sort by clicking on table header')
# st. dataframe(data=activity_fin[['Name of Subactivity','Cost of Subactivity in GNF','Amount of Finance Received','Gap']], width=1000)

# graph subactivity vs. cost of subactivity
sub_cost_fig = px.histogram(activity_fin, x = "Name of Subactivity",
                   y = "Cost of Subactivity in GNF",
                  orientation = 'v').update_xaxes (categoryorder="total ascending")

sub_fin_fig = px.histogram(activity_fin, y = "Name of Subactivity",
                   x = "Amount of Finance Received",
                  orientation = 'h').update_xaxes (categoryorder="total ascending")

# App Design
st.set_page_config(page_title='TIPAC',  layout='wide', page_icon=':hospital:')

# this is the header
t1, t2 = st.columns((0.07,1))

t1.image('index.png', width = 120)
t2.title("Tool for Integrated Planning and Costing (TIPAC)")
# t2.markdown(" **Phone:** 248-XXX-XXXX **| Website:** www.google.com **| Email:** joshiggins@deloitte.com")

# tab setup
tab1, tab2, tab3 = st.tabs(['Financing','Disease', 'Projections'])

with tab1:
    with st.spinner('Updating Report...'):
        with st.expander("Activity Cost Overview"):
            col1, col2 = st.columns([1.5,1])
            with col1:
                # graph activity vs. amount of finance received
                activ_cost_df = pd.DataFrame(activity_fin.groupby(by=['Name of Activity'], as_index=False)[['Cost of Subactivity in GNF', 'Amount of Finance Received']].sum())
                activ_cost_fig = go.Figure(data=[
                    go.Bar(name='Total Cost', x=activ_cost_df['Name of Activity'], y=activ_cost_df['Cost of Subactivity in GNF']),
                    go.Bar(name='Total Financing Received', x=activ_cost_df['Name of Activity'], y=activ_cost_df['Amount of Finance Received'])
                ])
                activ_cost_fig.update_layout(barmode='group',
                                             title='Cost and Financing by Activity')
                st.plotly_chart(activ_cost_fig)

            with col2:
                # plot pie chart for same data
                activ_cost_pie = px.pie(activ_cost_df, values='Cost of Subactivity in GNF', names='Name of Activity', title = 'Composition of Activity Costs')
                st.plotly_chart(activ_cost_pie)
                # st.image('Stacked_100_bar.png')
                # st.plotly_chart(sub_fin_fig)
                # st.plotly_chart(sub_cost_fig)
        with st.expander("Subactivity Detail"):
            st.subheader('Sort, filter, and group by clicking on table header')
            activ_stack_df = activity_fin[['Name of Activity',
                                           'Name of Subactivity',
                                           'Amount of Finance Received',
                                           'Cost of Subactivity in GNF',
                                           'Gap']]

            gb = GridOptionsBuilder.from_dataframe(activ_stack_df)
            k_sep_formatter = JsCode("""
               function(params) {
                   return (params.value == null) ? params.value : params.value.toLocaleString(); 
               }
               """)
            gb.configure_columns(['Amount of Finance Received', 'Cost of Subactivity in GNF', 'Gap'], valueFormatter=k_sep_formatter)
            gb.configure_default_column(groupable=True)
            gb.configure_side_bar()
            vgo = gb.build()
            AgGrid(activ_stack_df,
                   gridOptions=vgo,
                   theme = 'balham',
                   width=1000,
                   reload_data=True,
                   fit_columns_on_grid_load=True,
                   allow_unsafe_jscode= True)
        with st.expander("Donor Information"):
            sub_act = st.selectbox('Choose Detail Type',
                                   ['Subactivity', 'Activity'],
                                   help='Filter report to show subactivity or activity detail')
            #subactivity prep
            donor_cols = list(activity_fin.columns[4:].values)
            sub_cols = ['Name of Activity', 'Name of Subactivity', 'Amount of Finance Received']
            # activity prep
            if sub_act == 'Subactivity':
                st.table(activity_fin[sub_cols+donor_cols])
            if sub_act == 'Activity':
                # create df
                activ_don = pd.DataFrame(activity_fin.groupby(by=['Name of Activity'], as_index=False)[
                                                 ['Amount of Finance Received'] + donor_cols].sum())
                st.table(activ_don)
                # create pie chart
                # activ_don_pie = px.pie(activ_don, values='Amount of Finance Received', names=donor_cols, title = 'Donor Composition')
                # st.write(activ_don.sum(axis =0))

with tab2:
    with st.spinner('Updating Report...'):
        # Filtering to Region
        health_df = pd.read_excel('health-analytics-data.xlsx', sheet_name='regions')
        region_2 = st.selectbox('Choose Region', health_df, help='Filter report to show only one region')

        # Creating Header Box Data
        hd_db_0 = pd.read_excel('health-analytics-data.xlsx', sheet_name='disease_burden_1')
        nb_villages = hd_db_0['Number of Villages'][hd_db_0['Regions'] == region_2].max()
        nb_schools = hd_db_0['Number of Schools'][hd_db_0['Regions'] == region_2].max()
        total_population = round(hd_db_0['Total Population'][hd_db_0['Regions'] == region_2].max(), 2)

        # Creating Header Boxes
        m1, m2, m3, m4, m5 = st.columns((1, 1, 1, 1, 1))

        # Filling Header Boxes In
        m1.write('')
        m2.metric(label='Number of Villages', value=nb_villages)
        m3.metric(label='Number of Schools', value=nb_schools)
        m4.metric(label='Total Population', value=total_population)
        m5.write('')

        # Target Population
        g1, g2 = st.columns((1.5, 1.5))

        # Health Analytics Data - Target Population Tab Dataframe
        hd_tp = pd.read_excel('health-analytics-data.xlsx', sheet_name='target_pop')
        hd_tp = hd_tp[hd_tp['Region'] == region_2]

        # Lymphedema vs. Oncho
        plot = go.Figure(data=[go.Bar(
            name='LF Lymphedema Management',
            y=hd_tp['LF Lymphedema Management'],
            x=hd_tp['District']#,
            #marker=dict(color='darkseagreen'),
        ),
            go.Bar(
                name='Oncho Round 1',
                y=hd_tp['Oncho Round 1'],
                x=hd_tp['District'] #,
                #marker=dict(color='darkgrey'),
            )
        ])

        plot.update_layout(title_text="Lymphedema vs. Oncho",
                           title_x=0,
                           margin=dict(l=0, r=10, b=10, t=30),
                           xaxis_title='',
                           yaxis_title='Target Population Count',
                           template='seaborn')

        g1.plotly_chart(plot, use_container_width=True)

        # Adult vs. Child
        plot = go.Figure(data=[go.Bar(
            name='SCH School Age Children',
            y=hd_tp['SCH School Age Children'],
            x=hd_tp['District'],
        ),
            go.Bar(
                name='SCH High Risk Adult',
                y=hd_tp['SCH High Risk Adult'],
                x=hd_tp['District'],
            )
        ])

        plot.update_layout(title_text="Adult vs. Child",
                           title_x=0,
                           margin=dict(l=0, r=10, b=10, t=30),
                           xaxis_title='',
                           yaxis_title='Target Population Count',
                           template='seaborn')

        g2.plotly_chart(plot, use_container_width=True)

        # Choropleth
        g3, g4 = st.columns((3, 1))

        # Choropleth
        test_df = pd.read_excel('health-analytics-data.xlsx', sheet_name='geo_data')
        test_df = test_df[test_df['Regions'] == region_2]
        m = leafmap.Map(tiles="stamentoner", center=(10.984335, -10.964355), zoom=6)
        m.add_heatmap(
            test_df,
            latitude="Latitude",
            longitude="Longitude",
            value="Total Population",
            name="Total Population Map",
            title="Total Population Map",
            radius=25,
        )
        m.add_title("Total Population Map", align="left")
        m.to_streamlit(height=400)

with tab3:
    with st.spinner('Updating Report...'):
        # Filtering to Region
        health_df = pd.read_excel('health-analytics-data.xlsx', sheet_name='regions')
        region_1 = st.selectbox('Choose Region ', health_df, help='Filter report to show only one region')

        with st.expander("Five Year Projection of Medicine Need"):
            # Five-year projection of medicine
            g5, g6, g7 = st.columns((1.33, 1.33, 1.33))

            # Health Analytics Data - Disease Burden Tab Dataframe
            hd_db_1 = pd.read_excel('health-analytics-data.xlsx', sheet_name='disease_burden_1')
            hd_db_1 = hd_db_1[hd_db_1['Regions'] == region_1]

            # LF Disease Burden
            hd_lf_db = hd_db_1[hd_db_1['Disease Type'] == 'LF Disease Burden Code']

            # Oncho Disease Burden
            hd_on_db = hd_db_1[hd_db_1['Disease Type'] == 'Oncho Disease Burden Code']

            # SCH Disease Burden
            hd_sch_db = hd_db_1[hd_db_1['Disease Type'] == 'SCH Disease Burden Code']

            # STH Disease Burden
            hd_sth_db = hd_db_1[hd_db_1['Disease Type'] == 'STH Disease Burden Code']

            # Trachoma Disease Burden
            hd_tra_db = hd_db_1[hd_db_1['Disease Type'] == 'Trachoma Disease Burden Code']

            # Five-year projection of medicine
            # LF Disease Burden
            fig = px.line(hd_lf_db, y="Disease Burden", x="Year", color='Districts')

            fig.update_layout(title_text="LF Disease Burden",
                              title_x=0,
                              margin=dict(l=0, r=10, b=10, t=30),
                              xaxis_title='',
                              yaxis_title='Target Population Count',
                              template='seaborn')

            g5.plotly_chart(fig, use_container_width=True)

            # Oncho Disease Burden
            fig = px.line(hd_on_db, y="Disease Burden", x="Year", color='Districts')

            fig.update_layout(title_text="Oncho Disease Burden",
                              title_x=0,
                              margin=dict(l=0, r=10, b=10, t=30),
                              xaxis_title='',
                              yaxis_title='Target Population Count',
                              template='seaborn')

            g6.plotly_chart(fig, use_container_width=True)

            # SCH Disease Burden
            fig = px.line(hd_sch_db, y="Disease Burden", x="Year", color='Districts')

            fig.update_layout(title_text="SCH Disease Burden",
                              title_x=0,
                              margin=dict(l=0, r=10, b=10, t=30),
                              xaxis_title='',
                              yaxis_title='Target Population Count',
                              template='seaborn')

            g7.plotly_chart(fig, use_container_width=True)

            # Five-year projection of medicine - continued
            g8, g9 = st.columns((1.5, 1.5))

            # STH Disease Burden
            fig = px.line(hd_sth_db, y="Disease Burden", x="Year", color='Districts')

            fig.update_layout(title_text="STH Disease Burden",
                              title_x=0,
                              margin=dict(l=0, r=10, b=10, t=30),
                              xaxis_title='',
                              yaxis_title='Target Population Count',
                              template='seaborn')

            g8.plotly_chart(fig, use_container_width=True)

            # Trachoma Disease Burden
            fig = px.line(hd_tra_db, y="Disease Burden", x="Year", color='Districts')

            fig.update_layout(title_text="Trachoma Disease Burden",
                              title_x=0,
                              margin=dict(l=0, r=10, b=10, t=30),
                              xaxis_title='',
                              yaxis_title='Target Population Count',
                              template='seaborn')

            g9.plotly_chart(fig, use_container_width=True)
        with st.expander("Five Year Projection of Cost"):
            st.text("To Be Completed")




############# OTHER TABS #############################



# app_mode = st.sidebar('Select ')


# Thinking of plotting a line chart or bubble chart to show program cost, funding, and gap

# Extras
# activ_fin_df = pd.DataFrame(activity_fin.groupby(by = ['Name of Activity'], as_index = False)['Amount of Finance Received'].sum())
# fig = px.bar(x = activ_fin_df["Name of Activity"], y = activ_fin_df["Amount of Finance Received"])
# st.plotly_chart(fig)

# # Plot!
# st.plotly_chart(fig, use_container_width=True)


# In[ ]:




