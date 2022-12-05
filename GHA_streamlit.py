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
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
import re
# import pyodbc

# Importing partial packagesfrom geopy.exc import GeocoderTimedOut
# from geopy.geocoders import Nominatim

# Read in Data
activity_fin = pd.read_excel('FINAL Guinea TIPAC Hackathon Data Set.xlsx', 
             sheet_name = 'Financing of Activities')
activity_fin = activity_fin.rename(columns={'Amount of Finance Recevied': 'Amount of Finance Received'})
activity_fin.head()

# App Design
st.set_page_config(page_title='TIPAC',  layout='wide', page_icon=':hospital:')

# this is the header
t1, t2 = st.columns((0.07,1))

t1.image('index.png', width = 120)
t2.title("Tool for Integrated Planning and Costing (TIPAC)")

# tab setup
tab1, tab2, tab3, tab4 = st.tabs(['Financing','Disease by Region', 'Target Districts','Projections'])

with tab1:
    with st.spinner('Updating Report...'):
        with st.expander("Activity Cost Overview"):
            col1, col2 = st.columns([1.5,1])
            with col1:
                # graph activity vs. amount of finance received
                activ_cost_df = pd.DataFrame(activity_fin.groupby(by=['Name of Activity'], as_index=False)[['Cost of Subactivity in GNF', 'Amount of Finance Received', 'Gap']].sum())
                activ_cost_fig = go.Figure(data=[
                    go.Bar(name='Total Cost', x=activ_cost_df['Name of Activity'], y=activ_cost_df['Cost of Subactivity in GNF']),
                    go.Bar(name='Total Financing Received', x=activ_cost_df['Name of Activity'], y=activ_cost_df['Amount of Finance Received'])
                ])
                activ_cost_fig.update_layout(barmode='group',
                                             title='Cost and Financing by Activity')
                st.plotly_chart(activ_cost_fig)
                gap_df = activ_cost_df[activ_cost_df['Gap'] > 0]
                gap_df['Percent Gap (%)'] = gap_df['Gap']/gap_df['Cost of Subactivity in GNF']*100
                gap_bar = px.bar(gap_df, x='Name of Activity',
                       y='Percent Gap (%)',
                                 hover_data={'Gap':':,d'})
                gap_bar.update_layout(xaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(gap_bar)

            with col2:
                # plot pie chart for same data
                activ_cost_pie = px.pie(activ_cost_df, values='Cost of Subactivity in GNF', names='Name of Activity', title = 'Composition of Activity Costs')
                st.plotly_chart(activ_cost_pie)
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
                                   ['Subactivity', 'Activity', 'Donor'],
                                   help='Filter report to show level of detail by category')
            #subactivity prep
            donor_cols = list(activity_fin.columns[4:].values)
            sub_cols = ['Name of Activity', 'Name of Subactivity', 'Amount of Finance Received']
            # activity prep
            # create df
            activ_don = pd.DataFrame(activity_fin.groupby(by=['Name of Activity'], as_index=False)[
                                         ['Amount of Finance Received'] + donor_cols].sum())

            if sub_act == 'Subactivity':
                st.table(activity_fin[sub_cols+donor_cols])
            if sub_act == 'Activity':
                don_act_bar = px.bar(activ_don,
                                     x='Name of Activity',
                                     y=list(activ_don.columns[3:-1])+['Gap'])
                st.plotly_chart(don_act_bar, use_container_width=True)
                don_stack_bar = px.histogram(activ_don,
                                     x='Name of Activity',
                                     y=list(activ_don.columns[3:-1]) + ['Gap'],
                                     barnorm='percent')
                st.plotly_chart(don_stack_bar, use_container_width=True)
                # create pie chart
                # activ_don_pie = px.pie(activ_don, values='Amount of Finance Received', names=donor_cols, title = 'Donor Composition')
                # st.write(activ_don.sum(axis =0))
            if sub_act == 'Donor':
                don_tot = activ_don[donor_cols].transpose()
                don_tot['Totals'] = activ_don[donor_cols].sum()
                don_tot_pie = px.pie(don_tot, values='Totals', names=donor_cols, title = 'Composition of Donor Contributions')
                st.plotly_chart(don_tot_pie)


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

        #m1, m2, m3, m4, m5 = st.columns((1, 1, 1, 1, 1))

        # Filling Header Boxes In
        #m1.write('')
        #m2.metric(label='Number of Villages', value=nb_villages)
        #m3.metric(label='Number of Schools', value=nb_schools)
        #m4.metric(label='Total Population', value=total_population)
        #m5.write('')

        # Target Population
        #g1 = st.columns(1)

        # Health Analytics Data - Target Population Tab Dataframe
        hd_tp = pd.read_excel('health-analytics-data.xlsx', sheet_name='target_pop')
        hd_tp = hd_tp[hd_tp['Region'] == region_2]

        dist_pop = pd.read_excel('FINAL Guinea TIPAC Hackathon Data Set.xlsx',
                                 sheet_name='Projected_Population')
        ed_dist_df = dist_pop.loc[(dist_pop['Year'] == 2021) & (dist_pop['Regions'] == region_2),:]

        # Target Populations
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
        ),
            go.Bar(
                name='SCH School Age Children',
                y=hd_tp['SCH School Age Children'],
                x=hd_tp['District'],
        ),
            go.Bar(
                name='SCH High Risk Adults',
                y=hd_tp['SCH High Risk Adult'],
                x=hd_tp['District'],
        ),
            go.Bar(
                name='STH High Risk Adults',
                y=ed_dist_df['STH High risk adult'],
                x=ed_dist_df['Districts'],
        )])

        plot.update_layout(title_text="Targeted Population",
                           #title_x=0,
                           #margin=dict(l=0, r=10, b=10, t=30),
                           xaxis_title='',
                           yaxis_title='Target Population Count',
                           template='seaborn')

        st.plotly_chart(plot, use_container_width=True)

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
    dist_pop = pd.read_excel('FINAL Guinea TIPAC Hackathon Data Set.xlsx',
                             sheet_name='Projected_Population')
    district_1 = st.selectbox('Choose District of Interest', dist_pop['Districts'], help='Filter report to show only one district')
    curr_dist_df = dist_pop.loc[(dist_pop['Year']== 2021),]
    # st.table(curr_dist_df)


    # Creating Header Boxes
    d1, d2, d3, d4 = st.columns(4)

    # Filling Header Boxes In
    d1.metric(label='Region', value=curr_dist_df.loc[curr_dist_df['Districts']==district_1,'Regions'].unique()[0])
    d2.metric(label='Number of Villages', value=int(curr_dist_df.loc[(curr_dist_df['Districts'] ==district_1),'Number of Villages']))
    d3.metric(label='Number of Schools', value=int(curr_dist_df.loc[(curr_dist_df['Districts'] ==district_1),'Number of Schools']))
    d4.metric(label='Total Population', value=int(curr_dist_df.loc[(curr_dist_df['Districts'] ==district_1),'Total Population']))

    plt_x = curr_dist_df.loc[(curr_dist_df['Districts']== district_1),:]

    fig = px.bar(plt_x, x="Districts", y=list(curr_dist_df.columns[-11:-7]),
                 barmode='group',
                 title="Target Population by Disease")
    st.plotly_chart(fig)

    subact_lst = pd.read_excel('FINAL Guinea TIPAC Hackathon Data Set.xlsx',
                  sheet_name='Subactivity List')
    # special character handling
    subact_lst['Expense Location'] = list(subact_lst['Expense Location'].str.replace('é', 'e'))
    activ_don = pd.DataFrame(activity_fin.groupby(by=['Name of Activity'], as_index=False)[
                                 ['Amount of Finance Received'] + donor_cols].sum())
    subactiv_mrg = subact_lst.merge(activ_don, how='right')
    fltr_tab = subactiv_mrg.loc[subactiv_mrg['Expense Location'].str.contains(district_1),:]
    for val in ['Cost of Subactivity in GNF']+list(fltr_tab.columns[6:]):
        fltr_tab[val] = fltr_tab[val]/len(fltr_tab['Expense Location'])

    st.write('Subactivity by District')
    c1, c2 = st.columns(2)
    fltr_bar_1 = px.bar(fltr_tab, x='Name of Subactivity', y='Cost of Subactivity in GNF', orientation='h')
    fltr_bar_2 = px.bar(fltr_tab, x='Name of Subactivity', y=fltr_tab.columns[6:-2], barmode='group',orientation='h')
    c1.plotly_chart(fltr_bar_1, use_container_width= True)
    c2.plotly_chart(fltr_bar_2, use_container_width= True)


with tab4:
    with st.spinner('Updating Report...'):
        # Filtering to Region
        region_pro = st.selectbox('Choose Region ', dist_pop['Regions'].unique(), help='Filter report to show only one region')
        avail_dists = dist_pop.loc[dist_pop['Regions'] == region_pro,:]
        dist_pro = st.selectbox('Choose District', avail_dists['Districts'].unique(), help='Filter report to show only one district')
        with st.expander("Five Year Projection of Medicine Need (in Units)"):
            g5, g6 = st.columns(2)
            g7, g8 = st.columns(2)
            g9, g10 = st.columns(2)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-7], x='Year', color='Districts')
            g5.plotly_chart(fig, use_container_width=True)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-8], x='Year', color='Districts')
            g6.plotly_chart(fig, use_container_width=True)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-9], x='Year', color='Districts')
            g7.plotly_chart(fig, use_container_width=True)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-10], x='Year', color='Districts')
            g8.plotly_chart(fig, use_container_width=True)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-11], x='Year', color='Districts')
            g9.plotly_chart(fig, use_container_width=True)

        with st.expander("Five Year Cost Projection"):
            g5, g6 = st.columns(2)
            g7, g8 = st.columns(2)
            g9, g10 = st.columns(2)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-7], x='Year', color='Districts')
            g5.plotly_chart(fig, use_container_width=True)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-8], x='Year', color='Districts')
            g6.plotly_chart(fig)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-9], x='Year', color='Districts')
            g7.plotly_chart(fig)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-10], x='Year', color='Districts')
            g8.plotly_chart(fig)

            fig = px.line(avail_dists, y=list(dist_pop.columns)[-11], x='Year', color='Districts')
            g9.plotly_chart(fig)

        #dist_2 = st.selectbox('Choose Region', avail_dists, help='Filter report to show only one region')


            # Five-year projection of medicine


            # Projected Population Data
            # Plot Medicine Need by Region and District


            #g9.plotly_chart(fig, use_container_width=True)





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




