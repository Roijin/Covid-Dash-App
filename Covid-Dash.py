# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 10:30:57 2021

@author: 
"""

import pandas as pd
import dash 
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input,Output,State
from jupyter_dash import JupyterDash
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask

import numpy as np # library to handle data in a vectorized manner

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import requests # library to handle requests

from urllib.request import urlopen
from urllib.request import Request


app = JupyterDash(__name__)

app.config.suppress_callback_exceptions = True


#state_AT = pd.read_csv('C:/Users/Raihan/Downloads/JUPYTER LAB/state_AT.csv')
url = 'https://github.com/Roijin/Covid-Dash-App/blob/808bc92d8a4107a97f98ca836b5050e700aa798e/state_AT.csv?raw=true'

state_AT = pd.read_csv(url)

states = state_AT['code']
cells = state_AT['Cell_Num']
cases = state_AT['Total Cases']

q1,q2,q3 = state_AT['Cell_Num'].quantile([.25,.5,.75])
q4 = state_AT['Cell_Num'].max()

criteria = [state_AT['Cell_Num'].between(0, q1), state_AT['Cell_Num'].between(q1, q2),
            state_AT['Cell_Num'].between(q2, q3),state_AT['Cell_Num'].between(q3, q4+5)]
values = ['Very Low','Low', 'High','Very High']

cell_freq = np.select(criteria, values, 0)

state_AT['Cell_Freq'] = cell_freq



fig = go.Figure(data=go.Choropleth(
    locations = states,
    z = cases,
    locationmode='USA-states',
    text = (state_AT['state'], state_AT['Cell_Freq']),
    colorscale = 'Reds',
    autocolorscale=False,
    reversescale=False,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_tickprefix = '',
    colorbar_title = 'Number Of Cases',
))

fig.update_layout(
    title_text='2020 Covid Cases<br>(Hover for Details)',
    geo = dict(
        scope='usa',
        projection=go.layout.geo.Projection(type = 'albers usa'),
        showlakes=False, # lakes
        lakecolor='rgb(255, 255, 255)'),
)

CLIENT_ID = 'QHMPFV5VFPLL2N3UF0UGKSQ2XVMGPHUXMDMZFBFUP0PPQ344' # your Foursquare ID
CLIENT_SECRET = 'X0QPAQGESYIVG4FRNDJRSZKID5PFE20Z14JXCQSXFUUKTIY4' # your Foursquare Secret
ACCESS_TOKEN = 'HFDA5JHDCPMSOGDA5KTFW0ZMQSFENTZOCGF13ZSYXB0AXIVN' # your FourSquare Access Token
VERSION = '20180604'
LIMIT = 1000

def getNearbyVenues( lat, lon, radius=100000):
    
    venues_list=[]
    # create the API request URL
    url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
        CLIENT_ID, 
        CLIENT_SECRET, 
        VERSION, 
        lat, 
        lon, 
        radius, 
        LIMIT)
            
    # make the GET request
    results = requests.get(url).json()["response"]['groups'][0]['items']
        
    # return only relevant information for each nearby venue
    venues_list.append([(
        v['venue']['name'], 
        v['venue']['location']['lat'], 
        v['venue']['location']['lng'],  
        v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = [
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    nearby_unique = len(nearby_venues['Venue Category'].unique())
    
    return(nearby_venues, nearby_unique)

def computedata(state):
    

    lat = state_AT.loc[state_AT['state']==state, 'latitude'].iloc[0]
    lon = state_AT.loc[state_AT['state']==state, 'longitude'].iloc[0]
    case = state_AT.loc[state_AT['state']==state, 'Total Cases'].iloc[0]
    Cell_Freq = state_AT.loc[state_AT['state']==state, 'Cell_Freq'].iloc[0]
    Cell_Num = state_AT.loc[state_AT['state']==state, 'Cell_Num'].iloc[0]
    
    
    
    venues, unique = getNearbyVenues(lat, lon)
    

    
    return (venues, unique, case, Cell_Freq, Cell_Num)
    
states_list = state_AT['state']

app.layout = html.Div(children=[ 
                                # TODO1: Add title to the dashboard
                                html.H1('US Travel Dash', 
                                        style={'textAlign': 'center', 'color': '#503D36',
                                                            'font-size': 24}),
    
                                # REVIEW2: Dropdown creation
                                # Create an outer division 
                                html.Div([
                                    # Add an division
                                    html.Div([
                                        # Create an division for adding dropdown helper text for report type
                                        html.Div(
                                            [
                                            html.H2('US State:', style={'margin-right': '2em'}),
                                            ]
                                        ),
                                        # TODO2: Add a dropdown
                                        dcc.Dropdown(id='input-state', 
                                                                    options=[{'label': i, 'value': i} for i in states_list],
                                                                    placeholder='Select State',
                                                                    style={'width':'80%', 'padding':'3px', 'font-size': '20px', 
                                                                           'text-align-last' : 'center'})
                                        
                                    # Place them next to each other using the division style
                                    ], style={'display':'flex'}),
                                          ]),
                                
                                # Add Computed graphs
                                # REVIEW3: Observe how we add an empty division and providing an id that will be updated during callback
                                html.Div(dcc.Graph(figure=fig)),
    
                                html.Div([
                                        html.Div([html.H2('Cell Service:', style={'margin-right': '2em'}),
                                                  html.H2([ ], id='plot1', 
                                                          style={'textAlign': 'center', 'color': '#503D36',
                                                            'font-size': 24,'margin-right': '2em'})
                                                  ]),
                                        html.Div([html.H2('Unique Venue Types:', style={'margin-right': '2em'}),
                                                  html.H2([ ], id='plot2', 
                                                          style={'textAlign': 'center', 'color': '#503D36',
                                                            'font-size': 24,'margin-right': '2em'})
                                                  ])
                                ], style={'display': 'flex'}),
    
                                html.Div([], style={'display': 'flex'})
                                ])

@app.callback (Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children'),
               Input(component_id='input-state', component_property='value'))

def results(state):
    venues, unique, case, Cell_Freq, Cell_Num = computedata(state)
    return Cell_Freq, unique

if __name__ == '__main__':
    app.run_server(mode="inline", host="localhost",port=8015, debug=False, dev_tools_ui=False, dev_tools_props_check=False)
