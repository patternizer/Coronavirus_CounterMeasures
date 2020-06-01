# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# PROGRAM: countermeasures_app.py
#-----------------------------------------------------------------------
# Version 0.7
# 13 May, 2020
# Dr Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
#-----------------------------------------------------------------------

import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask
import os
from random import randint

#-----------------------------------------------------------------------
def discrete_colorscale(values, colors):
    """
    values - categorical values
    colors - rgb or hex colorcodes for len(values)-1
    returns - plotly  discrete colorscale, tickvals, ticktext
    """
    
    if len(values) != len(colors)+1:
        raise ValueError('len(values) should be = len(colors)+1')
    values = sorted(values)     
    nvalues = [(v-values[0])/(values[-1]-values[0]) for v in values]  #normalized values
    colorscale = []
    for k in range(len(colors)):
        colorscale.extend([[nvalues[k], colors[k]], [nvalues[k+1], colors[k]]])        
    tickvals = [((values[k]+values[k+1])/2.0) for k in range(len(values)-1)] 
    ticktext = [f'{int(values[k])}' for k in range(len(values)-1)]
    return colorscale, tickvals, ticktext
#-----------------------------------------------------------------------

# Define dictionary of counter-measures and deduce colorscale
countermeasures = {
'0': 'No or few containment measures in place',
'1': 'Ban on public gatherings, cancellation of major events and conferences',
'2': 'Schools and universities closed (dates matched to those from Unesco https://en.unesco.org/themes/education-emergencies/coronavirus-school-closures',
'3': 'Non-essential shops, restaurants and bars closed',
'4': 'Night curfew / partial lockdown in place for broad population categories',
'5': 'All-day lockdown / shelter-in-place government instruction (citizens allowed to venture come out for essential items',
#'6': 'Harsh lockdown (citizens forbidden to leave home even to buy essential items)'
}
nlabels = len(countermeasures)

# Import Coronavirus countermeasure data from Olivier Lejeune
"""
Daily updated Coronavirus containment measures taken by governments from 2020-01-23 to date
Provided by Olivier Lejeune: http://www.olejeune.com/ at:
https://github.com/OlivierLej/Coronavirus_CounterMeasures
dataset.csv has structure: country_id, country_name, 20200123_date, ...  
"""

url = r'https://raw.githubusercontent.com/OlivierLej/Coronavirus_CounterMeasures/master/dataset.csv'
#url = r'https://raw.githubusercontent.com/patternizer/Coronavirus_CounterMeasures/master/dataset.csv'
df = pd.read_csv(url)
country_name = df.country_name
country_id = df.country_id

# Import FIPS codes
"""
USA data is at state level and uses the alpha-2 code FIPS convention.
Country data uses the alpha-3 code FIPS convention.
Extract alpha-2 codes for countries and re-populate dataframe country_id
"""

fips = r'https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv'
df_fips = pd.read_csv(fips)
alpha_2_codes = df_fips['alpha-2']
alpha_3_codes = df_fips['alpha-3']
id_length = [len(country_id[i]) for i in range(0,len(country_id))]
usa = [i for i in range(len(country_id)) if id_length[i] < 3]
world = [i for i in range(len(country_id)) if id_length[i] > 2]
   
# Set date
""" 
Data is available from 2020-01-23 to date 
"""
headers = df.columns
for i in range(len(headers)-1):
    
    if i>1:   
        
        columnstr = headers[i][0:4] + '-' + headers[i][4:6] + '-' + headers[i][6:8]
        df.rename(columns = {headers[i]:columnstr}, inplace = True) 

timenow = pd.Timestamp.now().to_pydatetime()
timestr = timenow.strftime('%Y-%m-%d')
date = str(timenow.year) + '-' + str("{:02}".format(timenow.month)) + '-' + str("{:02}".format(timenow.day))
country_status = df[date]
datelist = df.columns[df.columns<=date]
opts = [{'label' : i, 'value' : i} for i in datelist]

# ========================================================================
# Start the App
# ========================================================================

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
app.config.suppress_callback_exceptions = True

app.layout = html.Div(children=[
            
# ------------
    html.H1(children='Coronavirus counter-measures: global status',            
            style={'padding' : '10px', 'width': '100%', 'display': 'inline-block'},
    ),
# ------------
            
# ------------
    html.Div([

        dbc.Row([

# ------------
            dbc.Col(html.Div([
                    
                dcc.Dropdown(
                    id = "input",
                    options = opts,           
                    value = date,
                    style = {'padding' : '10px', 'width': '40%', 'display': 'inline-block'},
                ),

#           dcc.Checklist(
#            dcc.RadioItems(
#                id = "check",  
#                options=[
#                    {'label': 'Equirectangular', 'value': 'equirectangular'},
#                    {'label': 'Natural Earth', 'value': 'natural earth'},
#                    {'label': 'Eckert-4', 'value': 'eckert4'},
#                    {'label': 'Mollweide', 'value': 'mollweide'},
#                    {'label': 'Sinusoidal', 'value': 'sinusoidal'},
#                    {'label': 'Albers USA', 'value': 'albers usa'}
#                ],
#                value = ['natural earth'],
#                value = 'natural earth',
#                labelStyle={'padding' : '3px', 'display': 'inline-block'},
#            )
                                    
            ]), 
            width={'size':8}, 
            ),
                        
# ------------
            dbc.Col(html.Div([

                dcc.RadioItems(
                    id = "radio",
                    options=[
                        {'label': ' Viridis', 'value': 'Viridis'},
                        {'label': ' Cividis', 'value': 'Cividis'},
                        {'label': ' Plotly3', 'value': 'Plotly3'},
                        {'label': ' Magma', 'value': 'Magma'},
                        {'label': ' Shikari', 'value': 'Shikari'}                        
                    ],
                    value = 'Shikari',
                    labelStyle={'padding' : '5px', 'display': 'inline-block'},
                ),
                               
            ]), 
            width={'size':4}, 
            ),
            
        ]),
    ]),
# ------------

# ------------
    html.Div([   

        dbc.Row([

# ------------
            dbc.Col(html.Div([
                dcc.Graph(id="output-graph", style = {'padding' : '0px', 'width': '100%', 'display': 'inline-block'}),  
            ]), 
            width={'size':8}, 
            ),
            
# ------------
            dbc.Col(html.Div([  
                                                    
# ------------
                dbc.Row(

                    html.P([
                        html.H3(children='Intervention levels'),
                        html.Div(children='0 = No or few containment measures in place'),
                        html.Div(children='1 = Ban on public gatherings, cancellation of major events and conferences'),
                        html.Div(children=['2 = Schools and universities closed (dates matched to those from ', html.A('UNESCO', href='https://en.unesco.org/themes/education-emergencies/coronavirus-school-closures'), ')']),
                        html.Div(children='3 = Non-essential shops, restaurants and bars closed'),
                        html.Div(children='4 = Night curfew / partial lockdown in place for broad population categories'),
                        html.Div(children='5 = All-day lockdown / shelter-in-place government instruction'),
                        #                    html.Div(children='6 = Harsh lockdown (citizens forbidden to leave home even to buy essential items)'),
                    ],
                    style = {'padding' : '20px', 'fontSize' : '12px', 'width': '100%', 'display': 'inline-block'}),   
                ),

# ------------
                dbc.Row(

                    html.P([
                        html.Div(children=['Data: ', html.A('Daily Status', href='https://github.com/OlivierLej/Coronavirus_CounterMeasures/blob/master/dataset.csv')]),    
                        html.Div(children=['Code: ', html.A('Github', href='https://github.com/patternizer/Coronavirus_CounterMeasures')]),       
                    ],
                    style = {'padding' : '20px', 'fontSize' : '15px', 'width': '100%', 'display': 'inline-block'}),                               
                ),

# ------------
                dbc.Row(

                    html.P([
                        html.Div(children=['Created by ', html.A('Michael Taylor', href='https://patternizer.github.io'),' using Plotly Dash Python']),            
                    ],
                    style = {'padding' : '10px', 'fontSize' : '15px', 'width': '100%', 'display': 'inline-block'}),                               
                ),
     
            ]), 
            width={'size':4}, 
            ),
                
        ]),
                        
    ]), 
# ------------

])

# ========================================================================
# Callbacks
# ========================================================================
           
@app.callback(
    Output(component_id='output-graph', component_property='figure'),
    [Input(component_id='input', component_property='value'), 
    Input(component_id='radio', component_property='value')],    
    )
    
def update_graph(value, colors):
    
    # Create Plotly figure
    """
    Plotly dash world map of country-level measures
    """
    if colors == 'Viridis':    
        cmap = px.colors.sequential.Viridis_r
    elif colors == 'Cividis':    
        cmap = px.colors.sequential.Cividis_r
    elif colors == 'Plotly3':
        cmap = px.colors.sequential.Plotly3_r
    elif colors == 'Magma':
        cmap = px.colors.sequential.Magma_r
    elif colors == 'Shikari':
#        cmap = ['#d8d7d5','#a1dcfc','#fdee03','#75b82b','#a84190','#0169b3']
        cmap = ['#2f2f2f','#a1dcfc','#fdee03','#75b82b','#a84190','#0169b3']                                
    cmap_idx = np.linspace(0,len(cmap)-1, nlabels, dtype=int)
    colors = [cmap[i] for i in cmap_idx]
    values = np.array(np.arange(len(colors)+1))
    colorscale, tickvals, ticktext = discrete_colorscale(values, colors)

#    projections_all = ['equirectangular', 'mercator', 'orthographic', 'natural earth', 'kavrayskiy7', 'miller', 'robinson', 'eckert4', 'azimuthal equal area', 'azimuthal equidistant', 'conic equal area', 'conic conformal', 'conic equidistant', 'gnomonic', 'stereographic', 'mollweide', 'hammer', 'transverse mercator', 'albers usa', 'winkel tripel', 'aitoff', 'sinusoidal']
#    projections_sub = ['equirectangular', 'natural earth', 'eckert4', 'mollweide', 'albers usa', 'sinusoidal']    
#    maptype = 'natural earth'   
#    if maptype == 'Equirectangular':
#        projection_type = 'equirectangular' 
#    elif maptype == 'Natural Earth':
#        projection_type = 'natural earth' 
#    elif maptype == 'Eckert-4':
#        projection_type = 'eckert4' 
#    elif maptype == 'Mollweide':
#        projection_type = 'mollweide' 
#    elif maptype == 'Sinusoidal':
#        projection_type = 'sinusoidal' 
#    elif maptype == 'Albers USA':
#        projection_type = 'albers usa' 
                
    data = [
    
    go.Choropleth(
            locations = df['country_id'][usa],
            text = df['country_name'][usa],
            z = df[value][usa],
            zmin = 0, 
            zmax = nlabels,
            locationmode='USA-states',
            colorscale = colorscale,
            colorbar = dict(thickness=15, tickvals=tickvals, ticktext=ticktext),
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_tickprefix = '',    
            colorbar_title = 'Level'),

    go.Choropleth(
            locations = df['country_id'][world],
            text = df['country_name'][world],
            z = df[value][world],
            zmin = 0, 
            zmax = nlabels,
            locationmode='ISO-3',   
            colorscale = colorscale,
            colorbar = dict(thickness=15, tickvals=tickvals, ticktext=ticktext),
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_tickprefix = '',
            colorbar_title = 'Level')
    ]

    layout = go.Layout(
                    
    title={
        'text': 'Coronavirus counter-measures: ' + value,
        'x':0.46,
        'y':0.95,
        'xanchor': 'center',
        'yanchor': 'top',
    },    
    geo=dict(
        scope = 'world',
        showframe = True,
        showcoastlines = True,
        projection_type = 'natural earth',
#       projection_type = 'equirectangular',
    ),
    annotations = [dict(
        text = 'Data: <a href="https://github.com/OlivierLej/Coronavirus_CounterMeasures">Olivier Lejeune</a>, Visualisation: <a href="https://patternizer.github.io">Michael Taylor</a>',
        x = 0.5, 
        y = -0.05, 
        xanchor = 'center',
        yanchor = 'bottom',
        showarrow = False,
        )
    ],
    margin=dict(r=0, l=0, b=40, t=40), 
    )
    
    return { 'data': data, 'layout':layout }
        
##################################################################################################
# Run the dash app
##################################################################################################

if __name__ == "__main__":
    app.run_server(debug=True)
    
