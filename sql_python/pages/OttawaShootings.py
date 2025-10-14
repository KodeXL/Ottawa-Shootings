import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, register_page, callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from sql_python.shooting_charts import update_input_container, yearly_stats_figs

load_figure_template('CYBORG')
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#registered page for multi-page app
register_page(__name__, name = "Yearly Stats", path='/')  # set the path to the root URL

# Initiaite a dash application
# app = dash.Dash(__name__, external_stylesheets= [dbc.themes.CYBORG],
#                 meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
                  
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Create the dropdown and multi select menu options
dropdown_options = [
     {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
     {'label': 'Overall Statistics', 'value': 'Overall Statistics'}
]
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
layout =  dbc.Container([
    # dbc.Row([
    #     dbc.Col(html.H1("Shootings Ottawa Dashboard", className="text-center"), width=12)
    # ]),
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col([     
            dcc.Dropdown(id='dropdown-statistics', options=dropdown_options, value = "Yearly Statistics", placeholder='Select Statistics')
        ], width=5, style={ 'color': 'black'}),
        dbc.Col([
            dcc.Input(id='input-year', type='number', placeholder= "Enter Year", min=2018, max=2024)
        ], width=1)
    ], className="mt-4 mb-4", justify='center'),           
    
    dbc.Row([ html.Div(id='graphs-container') 
    ], className="chart-box mb-4 mt-4"),
], fluid=True)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Add callback decorator                                
# Define the callback function to update the input container based on the selected statistics
@callback(
    [Output(component_id='input-year', component_property='value'),
    Output(component_id='input-year', component_property='disabled')],
    Input(component_id='dropdown-statistics',component_property='value')
)

def update_inputs(selected_statistics):
    return update_input_container(selected_statistics)
  
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Add callback decorator
# Define the callback function to update the output and map container based on the selected statistics
@callback(
    Output(component_id='graphs-container', component_property='children'), 
    [Input(component_id='dropdown-statistics', component_property='value'),
    Input(component_id='input-year', component_property='value')]
)

#add function to update the output container
def update_figs(selected_statistics, entered_year):
    return yearly_stats_figs(selected_statistics, entered_year)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
