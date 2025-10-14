import dash
from dash import dcc, html, callback, register_page
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output
from sql_python.shooting_charts import loi_stats_figs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

load_figure_template('CYBORG')

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
dropdown_options_loi = [ 
    {'label': 'FATAL',  'value': 'FATAL'},
     {'label': 'MAJOR', 'value': 'MAJOR'},
     {'label': 'MINOR', 'value': 'MINOR'},
     {'label': 'NONE', 'value': 'NONE'},
     {'label': 'UNKNOWN', 'value': 'UNKNOWN'},
     {'label': 'NOT APPLICABLE', 'value': 'NOT APPLICABLE'}
]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
#registered page for multi-page app
register_page(__name__, name = "Level of Injury Stats", path='/loi_stats_page')  #Set the path to the root URL

# # Initiaite a dash application 
# app = dash.Dash(__name__, external_stylesheets= [dbc.themes.CYBORG],
#                 meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
layout =  dbc.Container([
    # dbc.Row([
    #     dbc.Col(html.H1("Shootings Ottawa Dashboard", className="text-center"), width=12)
    # ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='loi-statistics', options=dropdown_options_loi, placeholder='Select Level of Injury', 
                value=[opt['value'] for opt in dropdown_options_loi],
                multi=True)
        ], width=5 , style={'color': 'black'})
    
    ], className="mt-4 mb-4", justify='center'),           
    dbc.Row([ html.Div(id='graph-container')], className="chart-box mt-4 mb-4"),
], fluid=True)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

@callback(
    Output(component_id='graph-container', component_property='children'), 
    Input(component_id='loi-statistics', component_property='value')
)

#add function to update the output container
def update_figs(entered_loi):
    return loi_stats_figs(entered_loi)



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
