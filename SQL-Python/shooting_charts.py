import pandas as pd
import plotly.express as px
import requests
import dash
from dash import dcc, html
from sqlalchemy import create_engine, text
import dash_bootstrap_components as dbc



#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Create an SQLAlchemy engine
user = 'root'
password = '20mnUXN5N5'
host = 'localhost'
database = 'Data'
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Create an SQLAlchemy engine
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM shootingsottawa"), con=conn)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#values
values = ['FATAL', 'MAJOR', 'MINOR', 'NONE', 'UNKNOWN', 'NOT APPLICABLE']

# Give occurred_months, in the dataframe df, an ordered categorical type
months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
df['Occurred_Month'] = pd.Categorical(df['Occurred_Month'], categories=months, ordered=True)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Assests 
legend_colors = {
    'FATAL': '#636EFA',
    'MAJOR': '#EF553B',
    'MINOR': '#00CC96',
    'NONE': '#AB63FA',
    'NOT APPLICABLE': '#19D3F3',
    'UNKNOWN': '#FFA15A'}

#Ward GeoJson Polygons
ward_layer  = 'https://open.ottawa.ca/datasets/ottawa::wards-2022-2026.geojson' 
response = requests.get(ward_layer)
ward_layer1 = response.json()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def update_input_container(selected_statistics):
    if selected_statistics =='Yearly Statistics': 
        return 2018, False                          # Enable year input, disable level of injury dropdown
    else: 
        return True, True                    # Disable both inputs
    
# def update_input_container(selected_statistics):
# if selected_statistics =='Yearly Statistics': 
#     return 2018, False, None, True                          # Enable year input, disable level of injury dropdown
# elif selected_statistics == 'Map Statistics':
#     return None, True, list(legend_colors.keys())[0:2], False     # *list(legend_colors.keys())* Disable year input, enable level of injury multiselect dropdown
# else: 
#     return None, True, None, True                          # Disable both inputs

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Add computation to callback function and return graph
def yearly_stats_figs(selected_statistics, entered_year):
    if selected_statistics == 'Yearly Statistics' and entered_year:
        df_peryear = df[df['Occurred_Year'] == int(entered_year)]
        df_month_peryear = df_peryear[['Occurred_Month', 'Level_of_Injury', 'ID']].groupby(['Occurred_Month','Level_of_Injury'], as_index=False).count() 
        pivot_month_peryear_df = df_month_peryear.pivot(index='Occurred_Month', columns='Level_of_Injury', values='ID')
        pivot_month_peryear_df = pivot_month_peryear_df.reset_index()         
        pivot_month_peryear_df_melted = pivot_month_peryear_df.melt(id_vars='Occurred_Month', var_name='Level_of_Injury', value_name='Number_of_Incidents')
        fig = px.bar(pivot_month_peryear_df_melted, x ='Occurred_Month', y = 'Number_of_Incidents',
            template = 'plotly_dark',
            color = 'Level_of_Injury',
            color_discrete_map = legend_colors,
            labels={"Level_of_Injury": "Level of Injury",
                "Occurred_Month" : 'Occurred Month',
                "Number_of_Incidents" : "Shooting Events"}
        )
        fig.update_layout(
            legend_title_text='', 
            font ={'size': 18 }, 
            hoverlabel= {'font_size': 20},
            title={'text': f"Number of Incidents per Month Grouped by Level of Injury in {entered_year}",
                'x': 0.5, 'y': 0.97,                                                                              # Center the title horizontally
                'xanchor': 'center'},                                                                   # Anchor the title to the center
            legend=dict(orientation="h",
            yanchor="top",
            y=1.10,
            xanchor="center",
            x=0.5
            ),
            margin=dict(t=130)
            )

        # Select data based on the entered year
        df_division_peryear = df_peryear[['Division', 'Level_of_Injury']].groupby('Division').count()
        df_division_peryear= df_division_peryear['Level_of_Injury'].sort_values(ascending =False)       # to series
            
            
        fig1 = px.bar(df_division_peryear, x =df_division_peryear.index, y = df_division_peryear.values,
                                template = 'plotly_dark',
                                text = df_division_peryear.values,
                                labels={"y" : 'Shooting Events'}
        )    
        fig1.update_traces(textposition='outside') 

        fig1.update_layout( 
            font ={'size': 18},
            hoverlabel= {'font_size': 20}, 
            title={
                'text': f"Shooting Events by Divison in {entered_year}",
                'x': 0.5,                                                                               # Center the title horizontally
                'xanchor': 'center'                                                                     # Anchor the title to the center
            }
        )       
        
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
        pivot_Top10N_df_peryear = pivot_Top10N_df_peryear.reset_index().rename(columns={'index': 'Neighbourhood' })
        pivot_Top10N_df_melted = pivot_Top10N_df_peryear.melt(id_vars='Neighbourhood', var_name='Level_of_Injury', value_name='Number_of_Incidents')

        fig2 = px.bar(pivot_Top10N_df_melted, x ='Neighbourhood' , y='Number_of_Incidents', color = 'Level_of_Injury',
                        template = 'plotly_dark',
                        #text_auto="true", 
                        labels={'Number_of_Incidents' : 'Number of Incidents', 'index':'Neighbourhood'}          
        )
        fig2.update_layout(
            legend_title_text='',
            font ={'size': 18},
            hoverlabel= {'font_size': 20},
            title={'text': f"Incidents by Neighbourhood Grouped by Level of Injury in {entered_year}",
                'x': 0.5,                                                   # Center the title horizontally
                'xanchor': 'center'                                         # Anchor the title to the center
            },
            legend=dict(orientation="h",
            yanchor="top",
            y=1.10,
            xanchor="center",
            x=0.5
            ),
            margin=dict(t=130)
            )
        
        # Select Ward and Councillor data based on the entered year
        df_ward_peryear = df_peryear[['Ward','Councillor','Level_of_Injury','ID']]\
            .groupby(['Ward','Councillor','Level_of_Injury']).count()    
        df_ward_peryear =df_ward_peryear.reset_index()
        top_10_wards_peryear = df_peryear[['Ward','Councillor']].value_counts().head(10)
        df_Top10Wards_peryear = df_ward_peryear.set_index('Ward').loc[top_10_wards_peryear.index.get_level_values('Ward')]
        df_Top10Wards_peryear = df_Top10Wards_peryear.reset_index()
        pivot_Top10Wards_peryear_df = df_Top10Wards_peryear.pivot(index=['Ward','Councillor'], columns='Level_of_Injury', values='ID')
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.reindex(index = top_10_wards_peryear.index, columns = pivot_Top10Wards_peryear_df.columns)
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.reset_index()
        pivot_Top10Wards_peryear_df['MultiIndexLabel'] =pivot_Top10Wards_peryear_df['Ward'].astype(str) + ' - ' + pivot_Top10Wards_peryear_df['Councillor']
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.drop(columns=['Councillor', 'Ward'])
        pivot_Top10Wards_peryear_df_melted = pivot_Top10Wards_peryear_df.melt(id_vars='MultiIndexLabel', var_name='Level_of_Injury', value_name='Number_of_Incidents')
        fig3 = px.bar(pivot_Top10Wards_peryear_df_melted, x ='MultiIndexLabel', y ='Number_of_Incidents', color = 'Level_of_Injury',
            template = 'plotly_dark',
            #text_auto="true", 
            labels={'Number_of_Incidents': 'Number of Incidents','MultiIndexLabel':'MultiIndexLabel - Ward, Councillor'}
        )
                    
        fig3.update_layout(
            legend_title_text='',
            font ={'size': 18},
            hoverlabel= {'font_size': 20},
            title={'text': f"Incidents by Ward and Councillor Grouped by Level of Injury in {entered_year}",
                'x': 0.5,                                                                               # Center the title horizontally
                'xanchor': 'center'                                                                     # Anchor the title to the center
            },
            legend=dict(orientation="h",
            yanchor="top",
            y=1.10,
            xanchor="center",
            x=0.5
            ),
            margin=dict(t=130)
            #height=1000                                                                                # Adjust height as needed
        
        )
        # Select location on Map based on the entered year
        fig4 = px.scatter_map(df_peryear,
            template = 'plotly_dark',
            lat=df_peryear.y,
            lon=df_peryear.x,
            hover_name='Neighbourhood',
            map_style ='open-street-map',
            labels={"x": "Longitude",
                "y":  'Latitude'},
            center = {"lat": 45.2515, "lon": -75.75},
            zoom=9.5
        )  

        fig4.update_traces(
            marker = {'size':11},
            hovertemplate= "<b>%{hovertext}</b><br><br>" +                                              # Country Name
                "<b>%{customdata[0]}</b><br>" + 
                "Councillor: %{customdata[1]}<br>"  +
                "Level of Injury: %{customdata[2]}<br>",   
                #"<extra></extra>",                                                # Remove the "trace name" that appears below the hover box
            customdata=df_peryear[['Ward','Councillor', 'Level_of_Injury' ]].values,
            hovertext=df_peryear['Neighbourhood'],
            hoverlabel ={'font_size':22}
        )
        fig4.update_layout(
            title={'text': f"Event Coordinates for {entered_year} Shootings", 'x': 0.5, 'font': {'size': 25} 
            },
            map_layers=[
                {
                'sourcetype': 'geojson',
                'source': ward_layer1,                                      # GeoJSON data loaded from the URL
                'type': 'line',                                             # Use 'line' to show ward boundaries
                'color': 'black',                                           # Color of the lines
                'line': {'width': 1.5}                                      # Width of the boundary lines
                }
            ]) 
        return [
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig), width={'size': 6}),
                dbc.Col(dcc.Graph(figure=fig1), width={'size': 6})
            ], className="charts mb-5"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig2), width={'size': 6}),
                dbc.Col(dcc.Graph(figure=fig3), width={'size': 6}) 
            ], className="charts mb-5"),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig4))
            ], className="mapcharts")
        ]
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
    else:
        if selected_statistics == 'Overall Statistics':
            # Create and display graphs for Overall Statistics
            # Level of Injury - Overall
            LoI = df['Level_of_Injury'].value_counts()
            fig10 = px.bar(LoI, x = LoI.index, y = LoI.values, text = LoI.values,
                template = 'plotly_dark',
                title='Shooting Events by Level of Injury',
                labels={"index": "Level of Injury", "y" : "Shooting Events"}
            )
            fig10.update_traces(textposition='outside') 

            fig10.update_layout( title_x = 0.25, font ={'size':18}, hoverlabel= {'font_size': 20} )

            # Time of day - Overall
            df_ToD = df['Time_of_Day'].value_counts()
            df_ToD = df_ToD.to_frame('Number of Incidents') 
            fig11 = px.pie(df_ToD, values ='Number of Incidents', names =df_ToD.index, hole=.25,
                template = 'plotly_dark',
                color = df_ToD.index,
                color_discrete_map = {df_ToD.index[0]: 'red', df_ToD.index[1]:'orange', df_ToD.index[2]:'green', df_ToD.index[3]: 'blue'},
                labels={"index" : 'Time of Day'},
                title= 'Shooting Events by Time of day'
                )
            fig11.update_layout(title_x = 0.5, font ={'size': 18}, hoverlabel= {'font_size': 20},
                legend=dict(orientation="h",
                yanchor="top",
                y=1.10,
                xanchor="center",
                x=0.5
                ),
                margin=dict(t=130),
                #height=1000  # Adjust height as needed
            )

            # Division - Overall
            df_division = df[['Division', 'Level_of_Injury']].groupby('Division').count()
            df_division = df_division['Level_of_Injury'].sort_values(ascending =False) # to series
            df_division = df_division.to_frame().reset_index()
            
            fig12 = px.bar(df_division, x ='Division', y = 'Level_of_Injury', 
                template = 'plotly_dark',
                text = 'Level_of_Injury',
                labels={"Level_of_Injury" : 'Shooting Events'},
                title= 'Shooting Events by Divison'
            )
            fig12.update_traces(textposition='outside') 

            fig12.update_layout(title_x= 0.5, font ={'size': 18}, hoverlabel= {'font_size': 20})     

            # Years - Overall
            df_years = df[['Occurred_Year', 'Level_of_Injury', 'ID']].groupby(['Occurred_Year','Level_of_Injury']).count()
            df_years= df_years.reset_index()
            pivot_df = df_years.pivot(index='Occurred_Year', columns='Level_of_Injury', values='ID')
            pivot_df = pivot_df.reset_index()
            pivot_df_melted = pivot_df.melt(id_vars='Occurred_Year', var_name='Level_of_Injury', value_name='Number_of_Incidents')
            fig13 = px.bar(pivot_df_melted, x ='Occurred_Year', y = 'Number_of_Incidents',
                template = 'plotly_dark',
                color = 'Level_of_Injury',
                #text_auto="true",
                color_discrete_map = legend_colors, 
                labels={"Occurred_Year" : 'Occurred Year',
                'Number_of_Incidents' : 'Number of Incidents'}                                  
            )
            fig13.update_layout(legend_title_text='',  font ={'size': 18}, hoverlabel= {'font_size': 20},
                title={'text': 'Shooting Events by Year',
                'x': 0.5,  # Center the title horizontally
                'y': 0.97,
                'xanchor': 'center'  # Anchor the title to the center         
                },
                legend=dict(orientation="h",
                yanchor="top",
                y=1.10,
                xanchor="center",
                x=0.5
                ),
                margin=dict(t=130)
            )
                    
            return [
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig10), width={'size': 6}),
                    dbc.Col(dcc.Graph(figure=fig11), width={'size': 6})
                ], className="charts mb-4"),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig12), width={'size': 6}),
                    dbc.Col(dcc.Graph(figure=fig13), width={'size': 6})
                ], className="charts mb-4"),
            ]
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def loi_stats_figs(entered_loi):    
#if entered_loi:
    df_LoI = df[df['Level_of_Injury'].isin(entered_loi)]
    
    title_text = (
        'All' if entered_loi and set(entered_loi) == set(values)
        else (', '.join(entered_loi).title() if entered_loi else 'None Selected')
    )     

    # Neighbourhood - Overall
    top10_neighborhoods_LoI = df_LoI['Neighbourhood'].value_counts().head(10)
    df_Neighbourhood_LoI = df_LoI[['Neighbourhood', 'Level_of_Injury','ID']].groupby(['Neighbourhood','Level_of_Injury']).count()
    df_Top10Neighbourhoods_LoI = df_Neighbourhood_LoI.reset_index()
    df_Top10Neighbourhoods_LoI = df_Top10Neighbourhoods_LoI.set_index('Neighbourhood').loc[top10_neighborhoods_LoI.index]
    df_Top10Neighbourhoods_LoI = df_Top10Neighbourhoods_LoI.reset_index()
    df_Top10Neighbourhoods_LoI.rename(columns = {'index':'Neighbourhood'}, inplace=True)
    pivot_Top10N_LoI_df = df_Top10Neighbourhoods_LoI.pivot(index='Neighbourhood', columns='Level_of_Injury', values='ID')
    pivot_Top10N_LoI_df = pivot_Top10N_LoI_df.reindex(index = top10_neighborhoods_LoI.index, columns = pivot_Top10N_LoI_df.columns)
    pivot_Top10N_LoI_df = pivot_Top10N_LoI_df.reset_index().rename(columns={'index': 'Neighbourhood' })
    pivot_Top10N_LoI_df_melted = pivot_Top10N_LoI_df.melt(id_vars='Neighbourhood', var_name='Level_of_Injury', value_name='Number_of_Incidents')
    fig5 = px.bar(pivot_Top10N_LoI_df_melted, x ='Neighbourhood', y = 'Number_of_Incidents',
        template = 'plotly_dark',
        color = 'Level_of_Injury',
        color_discrete_map = legend_colors,
        labels={'Number_of_Incidents' : 'Number of Incidents', 'index':'Neighbourhood'})
                    
    fig5.update_layout(
        title_x= 0.5, 
        title={'text': f'{title_text} <br>Shooting Events by Neighbourhood',
            'x': 0.5,                                                                                # Center the title horizontally
            'xanchor': 'center'},                                                                    # Anchor the title to the center}
        #margin=dict(t=120, b=60, l=40, r=40),
        font ={'size': 18},
        hoverlabel= {'font_size': 20}, 
        showlegend=False
    )

    # Ward/Councillor - LoI
    top10_wards_LoI = df_LoI[['Ward','Councillor']].value_counts().head(10)
    df_ward_LoI = df_LoI[['Ward','Councillor','Level_of_Injury','ID']].groupby(['Ward','Councillor','Level_of_Injury']).count()    
    df_ward_LoI =df_ward_LoI.reset_index()
    df_Top10Wards_LoI = df_ward_LoI.set_index('Ward').loc[top10_wards_LoI.index.get_level_values('Ward')]
    df_Top10Wards_LoI = df_Top10Wards_LoI.reset_index()
    pivot_Top10Wards_LoI_df = df_Top10Wards_LoI.pivot(index=['Ward','Councillor'], columns='Level_of_Injury', values='ID')
    pivot_Top10Wards_LoI_df = pivot_Top10Wards_LoI_df.reindex(index = top10_wards_LoI.index, columns = pivot_Top10Wards_LoI_df.columns)
    pivot_Top10Wards_LoI_df = pivot_Top10Wards_LoI_df.reset_index()
    pivot_Top10Wards_LoI_df['MultiIndexLabel'] =pivot_Top10Wards_LoI_df['Ward'].astype(str) + ' - ' + pivot_Top10Wards_LoI_df['Councillor']
    pivot_Top10Wards_LoI_df = pivot_Top10Wards_LoI_df.drop(columns=['Councillor','Ward'])
    pivot_Top10Wards_LoI_melted = pivot_Top10Wards_LoI_df.melt(id_vars='MultiIndexLabel', var_name='Level_of_Injury', value_name='Number_of_Incidents')

    fig6 = px.bar(pivot_Top10Wards_LoI_melted, x ='MultiIndexLabel', y ='Number_of_Incidents',
        template = 'plotly_dark',
        color = 'Level_of_Injury',
        color_discrete_map = legend_colors,
        labels={"Number_of_Incidents" : 'Shooting Events', 'MultiIndexLabel':'MultiIndexLabel - Ward, Councillor', 'variable': 'Level of Injury'})
        

    fig6.update_layout(
        title={'text': f'{title_text} <br> Shooting Events by Ward/Councillor ',
            'x': 0.5,                                                                               # Center the title horizontally
            'xanchor': 'center'},                                                                   # Anchor the title to the center
        #margin=dict(t=120, b=60, l=40, r=40),
        font ={'size': 18},
        hoverlabel= {'font_size': 20}, 
        showlegend=False)

    
    # Years - LoI
    df_years_LoI = df_LoI[['Occurred_Year', 'Level_of_Injury', 'ID']].groupby(['Occurred_Year','Level_of_Injury']).count()
    df_years_LoI= df_years_LoI.reset_index()
    pivot_df_LoI = df_years_LoI.pivot(index='Occurred_Year', columns='Level_of_Injury', values='ID')
    pivot_df_LoI = pivot_df_LoI.reset_index()
    pivot_df_LoI_melted = pivot_df_LoI.melt(id_vars='Occurred_Year', var_name='Level_of_Injury', value_name='Number_of_Incidents')
    
    fig7 = px.bar(pivot_df_LoI_melted, x ='Occurred_Year', y = 'Number_of_Incidents', 
        template = 'plotly_dark',
        color = 'Level_of_Injury',
        color_discrete_map = legend_colors, 
        labels={"Level_of_Injury": "Level of Injury",
            "Occurred_Year" : 'Occurred Year',
            "Number_of_Incidents" : "Shooting Events"}                                  
    )
    fig7.update_layout( showlegend=False,
        font ={'size': 18},
        hoverlabel= {'font_size': 20},
        #margin=dict(t=120, b=60, l=40, r=40),
        title={'text': f'{title_text} <br> Shooting Events by Year ',
            'x': 0.5,                                                                               
            'xanchor': 'center'}
    )


    # Month - LoI
    df_month_LoI = df_LoI[['Occurred_Month', 'Level_of_Injury', 'ID']].groupby(['Occurred_Month','Level_of_Injury']).count() 
    df_month_LoI = df_month_LoI.reset_index()
    pivot_month_LoI_df = df_month_LoI.pivot(index='Occurred_Month', columns='Level_of_Injury', values='ID')
    pivot_month_LoI_df = pivot_month_LoI_df.reset_index()
    pivot_month_LoI_df_melted = pivot_month_LoI_df.melt(id_vars='Occurred_Month', var_name='Level_of_Injury', value_name='Number_of_Incidents')
    fig8 = px.bar(pivot_month_LoI_df_melted, x ='Occurred_Month', y = 'Number_of_Incidents',
        template = 'plotly_dark',
        color = 'Level_of_Injury',
        color_discrete_map = legend_colors, 
        labels={"Level_of_Injury": "Level of Injury",
            "Occurred_Month" : 'Occurred Month',
            "Number_of_Incidents" : "Shooting Events"}
            )
    fig8.update_layout(
        showlegend=False,
        font ={'size': 18},
        hoverlabel= {'font_size': 20},
        #margin=dict(t=120, b=60, l=40, r=40),
        title={'text': f"{title_text} <br> Number of Incidents by Month",
            'x': 0.5,                                                                               # Center the title horizontally
            'xanchor': 'center'                                                                     # Anchor the title to the center
        }
    )

    fig9 = px.scatter_map(df_LoI,
        template = 'plotly_dark',
        lat=df_LoI.y,
        lon=df_LoI.x,
        hover_name='Neighbourhood',
        #hover_data = {'x':False, 'y':False,},# 'Neighbourhood':True,'Councillor':True},
        map_style ='open-street-map',
        labels={"x": "Longitude",
            "y":  'Latitude'},
        center = {"lat": 45.2515, "lon": -75.75},
        zoom=9.5
    )
    fig9.update_traces(
    marker = {'size':11},
    hovertemplate=  "<b>%{hovertext}</b><br><br>" +  # Country Name
        "<b>%{customdata[0]}</b><br>" + 
        "Councillor: %{customdata[1]}<br>"  +
        "Level of Injury: %{customdata[2]}<br>" + 
        "%{customdata[3]}<br>",  
    customdata=df_LoI[['Ward','Councillor', 'Level_of_Injury', 'Occurred_Year' ]].values,
    hovertext=df_LoI['Neighbourhood'],
    hoverlabel ={'font_size':22}
    )

    fig9.update_layout(
        title={'text': f"Event Coordinates for {title_text} Shootings", 'x': 0.5, 'font': {'size': 25}},  # Center the title horizontally
        map_layers=[{
        'sourcetype': 'geojson',
        'source': ward_layer1,  # GeoJSON data loaded from the URL
        'type': 'line',        # Use 'line' to show ward boundaries
        'color': 'black',       # Color of the lines
        'line': {'width': 1.5}   # Width of the boundary lines
        }]
    )

    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig5), width=6),
            dbc.Col(dcc.Graph(figure=fig6), width=6)
        ], className="charts mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig7), width=6),
            dbc.Col(dcc.Graph(figure=fig8), width=6)
        ], className="charts mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig9))
        ], className="mapcharts mt-4")
    ]
# else:
#     return None
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------    
    
 