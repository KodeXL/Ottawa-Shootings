import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from sorted_months_weekdays import *
from sort_dataframeby_monthorweek import *
import plotly.express as px
import json
import requests
import mysql.connector

conn = mysql.connector.connect(
        user = 'root',
        password = 'XXXXXXXXXX',
        host = 'localhost',
        database = 'Data' )
cursor = conn.cursor() 


df = pd.read_sql("SELECT * FROM loi", conn)

# List of years 
#year_list = [i for i in range(2018, 2023, 1)]

# Create a dash application layout
app = dash.Dash(__name__) #  

colors = {
    'background': '#111111',
    'text': '#7FDBFF'}

#---------------------------------------------------------------------------------
# Create the dropdown menu options
dropdown_options = [
     {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
     {'label': 'Overall Statistics', 'value': 'Overall Statistics'},
     {'label': 'Map Statistics',     'value': 'Map Statistics'}
]
dropdown_options_loi = [ 
    {'label': 'FATAL',  'value': 'FATAL'},
     {'label': 'MAJOR', 'value': 'MAJOR'},
     {'label': 'MINOR', 'value': 'MINOR'},
     {'label': 'NONE', 'value': 'NONE'},
     {'label': 'UNKNOWN', 'value': 'UNKNOWN'}

]
#---------------------------------------------------------------------------------------
#Ward GeoJson Polygons
ward_layer  = 'https://open.ottawa.ca/datasets/ottawa::wards-2022-2026.geojson' 
response = requests.get(ward_layer)
ward_layer1 = response.json()
#---------------------------------------------------------------------------------------

# Get the layout of the application and adjust it.
# Create an outer division using html.Div and add title to the dashboard using html.H1 component
# Add a html.Div and core input text component
# Finally, add graph component.
app.layout = html.Div([ 
    html.H1('Shootings Ottawa Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
   # Add two dropdown menus, one after the year
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            #value='Yearly Statistics',
            placeholder='Select Statistics'
        )
    ], style={'width': '30%', 'margin': 'auto'}),
    
    # Year input
        html.Div([ 
             dcc.Input(
            id='input-year', #value='2018', 
            type='number', 
            placeholder='Enter Year',
            min=2018,  # Minimum allowed value
            max=2023,  # Maximum allowed value
            style={'height':'25px', 'font-size': 17.5}
         )
    ], style={'width': '30%', 'margin': 'auto', 'padding': '10px'}),

        html.Div([
         dcc.Dropdown(
            id='loi-statistics',
            options=dropdown_options_loi,
            placeholder='Select Level of Injury'
        )
    ], style={'width': '30%', 'margin': 'auto'}),
    
        html.Br(),
        html.Br(),
    
    # Div for the top 4 graphs (2 per row)
        html.Div(id='output-container', style={   
         
         'display': 'flex',
         'flex-wrap': 'wrap',             # Stacking rows vertically         #'flex-direction': 'column',
         'width': '100%',                 # Take the full width of the page   #className='chart-grid',
         'padding': '10px',
         'justify-content': 'center'     # Center the charts horizontally                        
    }),

    # Map container at the bottom, full width
        html.Div(id='map-container', style={
        'width': '100%',  # Make the map span full width
        'height': '1000px',  # Increase map height
        'padding': '10px','gap': '100px','padding-bottom': '50px'
    })
], style={'font-size': 20})

# add callback decorator                                
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    [Output(component_id='input-year', component_property='value'),
    Output(component_id='input-year', component_property='disabled'),
    Output(component_id='loi-statistics', component_property='value'),
    Output(component_id='loi-statistics', component_property='disabled')],
    Input(component_id='dropdown-statistics',component_property='value'))

def update_input_container(selected_statistics):
    if selected_statistics =='Yearly Statistics': 
        return None, False, None, True
    elif selected_statistics == 'Map Statistics':
        return None, True, None, False
    else: 
        return None, True, None, True


# add callback decorator
# Define the callback function to update the output container based on the selected statistics
@app.callback(
    [Output(component_id='output-container', component_property='children'),
              Output(component_id='map-container', component_property='children')],
             [Input(component_id='dropdown-statistics', component_property='value'),
             Input(component_id='input-year', component_property='value'),
              Input(component_id='loi-statistics', component_property='value')])

# Add computation to callback function and return graph
def update_output_container(selected_statistics, entered_year, entered_loi):
    if selected_statistics == 'Overall Statistics':

      # Create and display graphs for Overall Statistics

      # Level of Injury - Overall
        LoI = df['Level_of_Injury'].value_counts()
        fig5 = px.bar(LoI, x = LoI.index, y = LoI.values, text = LoI.values,
                    title='Shooting Events by Level of Injury',
                        labels={"index": "Level of Injury", "y" : "Shooting Events"}
        )
        fig5.update_traces(textposition='outside') 

        fig5.update_layout( title_x = 0.25, font ={'size': 20}, hoverlabel= {'font_size': 27} )

      # Time of day - Overall
        df_ToD = df['Time_of_Day'].value_counts()
        df_ToD = df_ToD.to_frame('Number of Incidents') 
        fig6 = px.pie(df_ToD, values ='Number of Incidents', names =df_ToD.index, hole=.25,
                             labels={"index" : 'Time of Day'},
                             title= 'Shooting Events by Time of day'
             )
        fig6.update_layout( title_x = 0.25, font ={'size': 20}, hoverlabel= {'font_size': 27})

        row_3 = html.Div([
            dcc.Graph(figure=fig5,  style={'flex-basis': '49%'}),
            dcc.Graph(figure=fig6,  style={'flex-basis': '49%'})
            ], style={'display': 'flex', 'gap': '100px', 'height':'750px'})

      # Division - Overall
        df_division = df[['Division', 'Level_of_Injury']].groupby('Division').count()
        df_division = df_division['Level_of_Injury'].sort_values(ascending =False) # to series
        df_division = df_division.to_frame().reset_index()
        
        fig7 = px.bar(df_division, x ='Division', y = 'Level_of_Injury', 
                                text = 'Level_of_Injury',
                                labels={"Level_of_Injury" : 'Shooting Events'},
                                title= 'Shooting Events by Divison'
)
   

        fig7.update_layout(title_x= 0.5, font ={'size': 20} , hoverlabel= {'font_size': 27})     

        # Years - Overall
        df_years = df[['Occurred_Year', 'Level_of_Injury', 'ID']].groupby(['Occurred_Year','Level_of_Injury']).count()
        df_years= df_years.reset_index()
        pivot_df = df_years.pivot(index='Occurred_Year', columns='Level_of_Injury', values='ID')

        fig8 = px.bar(pivot_df, x =pivot_df.index, y = pivot_df.columns, labels={#"variable": "Level of Injury",
                                                # "Occurred_Month" : 'Occurred Month',
                                                 "value" : "Shooting Events"}                                  
        )
        fig8.update_layout(font ={'size': 20}, hoverlabel= {'font_size': 27},
                           title={
                            'text': 'Shooting Events by Year',
                            'x': 0.3,  # Center the title horizontally
                            'xanchor': 'center'  # Anchor the title to the center               
        })
        
        #chart9 = dcc.Graph(figure=fig8)
        
        row_4 = html.Div([
                            dcc.Graph(figure=fig7,  style={'flex-basis': '49%'}),
                            dcc.Graph(figure=fig8,  style={'flex-basis': '49%'})
            ], style={'display': 'flex', 'gap': '100px', 'height':'750px'})
        
        # Neighbourhood - Overall
        overall_top_10_neighborhoods = df['Neighbourhood'].value_counts().head(10)
        df_Neighbourhood_overall = df[['Neighbourhood', 'Level_of_Injury','ID']].groupby(['Neighbourhood','Level_of_Injury']).count()
        df_Top10Neighbourhoods_overall = df_Neighbourhood_overall.reset_index()
        df_Top10Neighbourhoods_overall = df_Top10Neighbourhoods_overall.set_index('Neighbourhood').loc[overall_top_10_neighborhoods.index]
        df_Top10Neighbourhoods_overall = df_Top10Neighbourhoods_overall.reset_index()
        df_Top10Neighbourhoods_overall.rename(columns = {'index':'Neighbourhood'}, inplace=True)
        pivot_Top10N_overall_df = df_Top10Neighbourhoods_overall.pivot(index='Neighbourhood', columns='Level_of_Injury', values='ID')
        pivot_Top10N_overall_df = pivot_Top10N_overall_df.reindex(index = overall_top_10_neighborhoods.index, columns = pivot_Top10N_overall_df.columns)
        
        fig9 = px.bar(pivot_Top10N_overall_df, x =pivot_Top10N_overall_df.index, y =pivot_Top10N_overall_df.columns,
                        labels={"value" : 'Shooting Events', 'index':'Neighbourhood'},
                        title= 'Shooting Events by Neighbourhood')
        fig9.update_layout(title_x= 0.25, font ={'size': 20}, hoverlabel= {'font_size': 27})
        
        # Ward/Councillor - Overall
        top_10_wards_overall = df[['Ward','Councillor']].value_counts().head(10)
        df_ward_overall = df[['Ward','Councillor','Level_of_Injury','ID']].groupby(['Ward','Councillor','Level_of_Injury']).count()    
        df_ward_overall =df_ward_overall.reset_index()
        df_Top10Wards_overall = df_ward_overall.set_index('Ward').loc[top_10_wards_overall.index.get_level_values('Ward')]
        df_Top10Wards_overall = df_Top10Wards_overall.reset_index()
        pivot_Top10Wards_overall_df = df_Top10Wards_overall.pivot(index=['Ward','Councillor'], columns='Level_of_Injury', values='ID')
        pivot_Top10Wards_overall_df = pivot_Top10Wards_overall_df.reindex(index = top_10_wards_overall.index, columns = pivot_Top10Wards_overall_df.columns)
        pivot_Top10Wards_overall_dfb = pivot_Top10Wards_overall_df.reset_index()
        pivot_Top10Wards_overall_dfb['MultiIndexLabel'] =pivot_Top10Wards_overall_dfb['Ward'].astype(str) + ' - ' + pivot_Top10Wards_overall_dfb['Councillor']
        pivot_Top10Wards_overall_dfa = pivot_Top10Wards_overall_df.reset_index().set_index('Ward')
        pivot_Top10Wards_overall_dfa = pivot_Top10Wards_overall_dfa.drop(columns='Councillor')

        fig10 = px.bar(pivot_Top10Wards_overall_dfb, x ='MultiIndexLabel', y =pivot_Top10Wards_overall_dfa.columns,
            labels={"value" : 'Shooting Events', 'MultiIndexLabel':'MultiIndexLabel - Ward, Councillor', 'variable': 'Level of Injury'},
            title= 'Shooting Events by Ward/Councillor')

        fig10.update_layout(title_x= 0.2, font ={'size': 20}, hoverlabel= {'font_size': 27})

        row_5 = html.Div([
                            dcc.Graph(figure=fig9,  style={'flex-basis': '49%'}),
                            dcc.Graph(figure=fig10,  style={'flex-basis': '49%'})
            ], style={'display': 'flex', 'gap': '100px', 'height':'1000px'})

        return [
                [html.Div([row_4, row_3], style={'display': 'flex', 'flex-direction': 'column', 'gap': '100px', 'height':'1500px','width': '80%'})],
                html.Div([row_5])
                ]
    
#style={'display': 'flex', 'flex-direction': 'column', 'gap': '100px', 'height':'1500px','width': '80%'}
    elif selected_statistics == 'Yearly Statistics' and entered_year:
        df_peryear = df[df['Occurred_Year'] == int(entered_year)]
        
        # Select data based on the entered year
        
        df_month_peryear = df_peryear[['Occurred_Month', 'Level_of_Injury', 'ID']].groupby(['Occurred_Month','Level_of_Injury']).count() 
        df_month_peryear = df_month_peryear.reset_index()
        pivot_month_peryear_df = df_month_peryear.pivot(index='Occurred_Month', columns='Level_of_Injury', values='ID')
        pivot_month_peryear_df = pivot_month_peryear_df.reset_index()
        pivot_month_peryear_df = Sort_Dataframeby_Month(df=pivot_month_peryear_df,monthcolumnname='Occurred_Month')
        pivot_month_peryear_df = pivot_month_peryear_df.set_index('Occurred_Month')

        
        fig = px.bar(pivot_month_peryear_df, x =pivot_month_peryear_df.index, y = pivot_month_peryear_df.columns, 
                                labels={"variable": "Level of Injury",
                                        "Occurred_Month" : 'Month Occurred',
                                        "value" : "Shooting Events"}
                )
        
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'], 
            font_color=colors['text'],
            autosize=True, 
            font ={'size': 20}, 
            hoverlabel= {'font_size': 27},
            title={'text': f"Number of Incidents per Month Grouped by Level of Injury in {entered_year}",
                                            'x': 0.5,  # Center the title horizontally
                                            'xanchor': 'center',  # Anchor the title to the center
                            
                })
        
            
        # Select data based on the entered year
        df_division_peryear = df_peryear[['Division', 'Level_of_Injury']].groupby('Division').count()
        df_division_peryear= df_division_peryear['Level_of_Injury'].sort_values(ascending =False) # to series
            
            
        fig1 = px.bar(df_division_peryear, x =df_division_peryear.index, y = df_division_peryear.values, 
                                text = df_division_peryear.values,
                                labels={"y" : 'Shooting Events'}
                )    

        fig1.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'], 
            font_color=colors['text'],
            autosize=True, 
            font ={'size': 20},
            hoverlabel= {'font_size': 27}, 
            title={'text': f"Shooting Events by Divison in {entered_year}",
                                            'x': 0.5,  # Center the title horizontally
                                            'xanchor': 'center'  # Anchor the title to the center
                })       
        
        # Select data based on the entered year
        df_Neighbourhood_peryear = df_peryear[['Neighbourhood', 'Level_of_Injury','ID']]\
                    .groupby(['Neighbourhood','Level_of_Injury']).count()    #.nlargest(:,'ID')#.sort_values('Level of Injury')
        top_10_neighborhoods_peryear = df_peryear['Neighbourhood'].value_counts().head(10)#.index

        df_Top10Neighbourhoods_peryear = df_Neighbourhood_peryear.reset_index()
        df_Top10Neighbourhoods_peryear = df_Top10Neighbourhoods_peryear.set_index('Neighbourhood').loc[top_10_neighborhoods_peryear.index]
        df_Top10Neighbourhoods_peryear = df_Top10Neighbourhoods_peryear.reset_index()
        df_Top10Neighbourhoods_peryear.rename(columns = {'index':'Neighbourhood'}, inplace=True)
        
        pivot_Top10N_df_peryear = df_Top10Neighbourhoods_peryear.pivot(index='Neighbourhood', columns='Level_of_Injury', values='ID')
        pivot_Top10N_df_peryear = pivot_Top10N_df_peryear.reindex(index = top_10_neighborhoods_peryear.index, columns = pivot_Top10N_df_peryear.columns)

        fig2 = px.bar(pivot_Top10N_df_peryear, x =pivot_Top10N_df_peryear.index, y =pivot_Top10N_df_peryear.columns,
                        labels={"value" : 'Shooting Events', 'index':'Neighbourhood'}
                        
        )
        
        fig2.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'], 
            font_color=colors['text'],
            autosize=True,
            font ={'size': 20},
            hoverlabel= {'font_size': 27},
            title={'text': f"Incidents by Neighbourhood Grouped by Level of Injury in {entered_year}",
                                            'x': 0.5,  # Center the title horizontally
                                            'xanchor': 'center'  # Anchor the title to the center
        })
        
        # Select data based on the entered year
        df_ward_peryear = df_peryear[['Ward','Councillor','Level_of_Injury','ID']]\
                    .groupby(['Ward','Councillor','Level_of_Injury']).count()    
        df_ward_peryear =df_ward_peryear.reset_index()
        top_10_wards_peryear = df_peryear[['Ward','Councillor']].value_counts().head(10)
        df_Top10Wards_peryear = df_ward_peryear.set_index('Ward').loc[top_10_wards_peryear.index.get_level_values('Ward')]
        df_Top10Wards_peryear = df_Top10Wards_peryear.reset_index()
        pivot_Top10Wards_peryear_df = df_Top10Wards_peryear.pivot(index=['Ward','Councillor'], columns='Level_of_Injury', values='ID')
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.reindex(index = top_10_wards_peryear.index, columns = pivot_Top10Wards_peryear_df.columns)
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.reset_index()
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.set_index('Ward')
        pivot_Top10Wards_peryear_dfa = pivot_Top10Wards_peryear_df.drop(columns='Councillor')
        pivot_Top10Wards_peryear_dfb = pivot_Top10Wards_peryear_df.reset_index()
        pivot_Top10Wards_peryear_dfb['MultiIndexLabel'] =pivot_Top10Wards_peryear_dfb['Ward'].astype(str) + ' - ' + pivot_Top10Wards_peryear_dfb['Councillor']

        fig3 = px.bar(pivot_Top10Wards_peryear_dfb, x ='MultiIndexLabel', y =pivot_Top10Wards_peryear_dfa.columns,
                        labels={"value" : 'Shooting Events', "variable": "Level of Injury",'MultiIndexLabel':'MultiIndexLabel - Ward, Councillor'},
                        title= 'Number of Shooting Events by Neighbourhood per Year')
        
        fig3.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'], 
            font_color=colors['text'], 
            autosize=True,
            font ={'size': 20},
            hoverlabel= {'font_size': 27},
            title={'text': f"Incidents by Ward and Councillor Grouped by Level of Injury in {entered_year}",
                                            'x': 0.5,  # Center the title horizontally
                                            'xanchor': 'center'  # Anchor the title to the center
        })

        # Row 1: First and Second graph
        row_1 = html.Div([
            dcc.Graph(figure=fig, style={'flex-basis': '49%'}),
            dcc.Graph(figure=fig1, style={'flex-basis': '49%'})
            ], style={'display': 'flex', 'gap': '100px', 'height':'750px'})  # Gap between graphs
        
        # Row 2: Third and Fourth graph
        row_2 = html.Div([
            dcc.Graph(figure=fig2, style={'flex-basis': '49%'}),
            dcc.Graph(figure=fig3, style={'flex-basis': '49%'})
            ], style={'display': 'flex', 'gap': '100px','height':'750px'})
        

        # Select data based on the entered year
        fig4 = px.scatter_mapbox(df_peryear,
                            lat=df_peryear.y,
                            lon=df_peryear.x,
                            hover_name='Neighbourhood',
                            mapbox_style ='open-street-map',
                            labels={"x": "Longitude",\
                                    "y":  'Latitude'},
                            center = {"lat": 45.2515, "lon": -75.6972},
                            zoom=10.2
        )  

        fig4.update_traces(
            marker = {'size':12},
            hovertemplate= "<b>%{hovertext}</b><br><br>" +  # Country Name
                    "<b>%{customdata[0]}</b><br>" + 
                    "Councillor: %{customdata[1]}<br>"  +
                    "Level of Injury: %{customdata[2]}<br>",   
                    #"<extra></extra>",  # Remove the "trace name" that appears below the hover box
            customdata=df_peryear[['Ward','Councillor', 'Level_of_Injury' ]].values,
            hovertext=df_peryear['Neighbourhood'],
            hoverlabel ={'font_size':25}
        )

        fig4.update_layout(font ={'size': 20},
            title={'text': f"Event Coordinates for {entered_year} Shootings", 'x': 0.5 
            },
            mapbox_layers=[
                {
                'sourcetype': 'geojson',
                'source': ward_layer1,  # GeoJSON data loaded from the URL
                'type': 'line',        # Use 'line' to show ward boundaries
                'color': 'black',       # Color of the lines
                'line': {'width': 1.5}   # Width of the boundary lines
                }
            ]) 
        chart5  = dcc.Graph(figure=fig4, style={'height': '1500px', 'width': '100%'})

        return [ 
                [html.Div([row_1], style={'height':'850px','width': '100%'})],
                html.Div([row_2, html.Br(), html.Br(), chart5], style={'height':'3000px','width': '100%'}) 
            ]

    #, style={'display': 'flex', 'flex-direction': 'column', 'gap': '100px', 'height':'800px','width': '80%'})
    elif selected_statistics=='Map Statistics' and entered_loi:
        df_LoI= df[df['Level_of_Injury'] == entered_loi]

        fig11 = px.scatter_mapbox(df_LoI,
                            lat=df_LoI.y,
                            lon=df_LoI.x,
                            hover_name='Neighbourhood',
                            #hover_data = {'x':False, 'y':False,},# 'Neighbourhood':True,'Councillor':True},
                            mapbox_style ='open-street-map',
                            labels={"x": "Longitude",
                                    "y":  'Latitude'},
                            center = {"lat": 45.2515, "lon": -75.6972},
                            zoom=10.2)

        fig11.update_traces(
        marker = {'size':13.5},
        hovertemplate= "<b>%{hovertext}</b><br><br>" +  # Country Name
                        "<b>%{customdata[0]}</b><br>" + 
                        "Councillor: %{customdata[1]}<br>"  +
                        "Level of Injury: %{customdata[2]}<br>" + 
                        "%{customdata[3]}<br>",  
        customdata=df_LoI[['Ward','Councillor', 'Level_of_Injury', 'Occurred_Year' ]].values,
        hovertext=df_LoI['Neighbourhood'],
        hoverlabel ={'font_size':30}
        )

        fig11.update_layout(font ={'size': 20},
            title={'text': f"Event Coordinates for {entered_loi} Shootings", 'x': 0.5  # Center the title horizontally
            },
            mapbox_layers=[
            {
            'sourcetype': 'geojson',
            'source': ward_layer1,  # GeoJSON data loaded from the URL
            'type': 'line',        # Use 'line' to show ward boundaries
            'color': 'black',       # Color of the lines
            'line': {'width': 2}   # Width of the boundary lines
            }
            ])


        return [None ,html.Div(dcc.Graph(figure=fig11, style={'height': '1500px', 'width': '100%'}))]  
    
    else:
            return [html.Div(), None]

#Run the application                   
if __name__ == '__main__':
    app.run_server(debug = False)