# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# PROGRAM: countermeasures_video.py
#-----------------------------------------------------------------------
# Version 0.2
# 31 July, 2020
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

import glob
from PIL import Image

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

#-----------------------------------------------------------------------
# Define dictionary of counter-measures and deduce colorscale
#-----------------------------------------------------------------------
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
#cmap = px.colors.sequential.Viridis_r
#cmap = px.colors.sequential.Cividis_r
#cmap = px.colors.sequential.Plotly3_r
#cmap = px.colors.sequential.Magma_r
#cmap = ['#d8d7d5','#a1dcfc','#fdee03','#75b82b','#a84190','#0169b3']
cmap = ['#2f2f2f','#a1dcfc','#fdee03','#75b82b','#a84190','#0169b3']
cmap_idx = np.linspace(0,len(cmap)-1, nlabels, dtype=int)
colors = [cmap[i] for i in cmap_idx]
values = np.array(np.arange(len(colors)+1))
colorscale, tickvals, ticktext = discrete_colorscale(values, colors)
#-----------------------------------------------------------------------

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
Data is available from 2020-01-23 to 2020-07-30 
"""
headers = df.columns
for i in range(len(headers)-1):
    
    if i>1:   
        
        columnstr = headers[i][0:4] + '-' + headers[i][4:6] + '-' + headers[i][6:8]
        df.rename(columns = {headers[i]:columnstr}, inplace = True) 

timenow = pd.Timestamp.now().to_pydatetime()
timestr = timenow.strftime('%Y-%m-%d')
# date = str(timenow.year) + '-' + str("{:02}".format(timenow.month)) + '-' + str("{:02}".format(timenow.day))
# Last entry to database: 2020-07-39' --> need to override timenow()
date = '2020-07-30'
country_status = df[date]
datelist = df.columns[df.columns<=date]
opts = [{'label' : i, 'value' : i} for i in datelist]

# PLOT WORLD STATUS FRAMES:
"""
Loop through plotly world daily maps of country-level measures
"""

#projections_all = ['equirectangular', 'mercator', 'orthographic', 'natural earth', 'kavrayskiy7', 'miller', 'robinson', 'eckert4', 'azimuthal equal area', 'azimuthal equidistant', 'conic equal area', 'conic conformal', 'conic equidistant', 'gnomonic', 'stereographic', 'mollweide', 'hammer', 'transverse mercator', 'albers usa', 'winkel tripel', 'aitoff', 'sinusoidal']
#projections_sub = ['equirectangular', 'natural earth', 'eckert4', 'mollweide', 'albers usa', 'sinusoidal']
projections = ['natural earth']
            
for j in range(len(projections)):

    for i in range(len(datelist)):

        date = datelist[i]
    
        fig = go.Figure(data=[
    
        go.Choropleth(
        locations = df['country_id'][usa],
        text = df['country_name'][usa],
        z = df[date][usa],
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
        z = df[date][world],
        zmin = 0, 
        zmax = nlabels,
        locationmode='ISO-3',   
        colorscale = colorscale,
        colorbar = dict(thickness=15, tickvals=tickvals, ticktext=ticktext),
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_tickprefix = '',
        colorbar_title = 'Level')])

        fig.update_layout(

        title={
            'text': 'Coronavirus counter-measures: ' + date,
            'x':0.46,
            'y':0.9,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        geo=dict(
            scope = 'world',
            showframe = True,
            showcoastlines = True,
            projection_type = projections[j]
        ),
        annotations = [dict(
            text = 'Data: <a href="https://github.com/OlivierLej/Coronavirus_CounterMeasures">Olivier Lejeune</a>, Visualisation: <a href="https://patternizer.github.io">Michael Taylor</a>',
            x = 0.5, 
            y=  0.0, 
            xanchor = 'center',
            yanchor = 'bottom',
            showarrow = False,
            )
        ],
        margin=dict(r=0, l=0, b=40, t=40), 
        )

        fig.write_image('countermeasures_'+ date +'.png')

    fp_in = "countermeasures_*.png"
    fp_out = "countermeasures_" + projections[j] + ".gif"

    img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
    img.save(fp=fp_out, format='GIF', append_images=imgs,
         save_all=True, duration=200, loop=0)

#-----------------------------------------------------------------------------------------------

print('** END')


