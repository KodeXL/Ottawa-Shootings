import pandas as pd
import plotly.express as px
import requests
import dash
from dash import dcc, html
from sqlalchemy import create_engine, text
import dash_bootstrap_components as dbc



#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Create an SQLAlchemy engine
# user = 'root'
# password = 'XXXXXXXXX'
# host = 'localhost'
# database = 'Data'
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Create an SQLAlchemy engine
# engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

# with engine.connect() as conn:
#     df = pd.read_sql(text("SELECT * FROM shootingsottawa"), con=conn)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
df = pd.read_csv("https://raw.githubusercontent.com/KodeXL/Ottawa-Shootings/refs/heads/main/sql_python/assets/shootingsottawa.csv")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Add ShortLabel and FullLabel columns
def shorten_neighbourhood(name):
    parts = [p.strip() for p in name.split('-')]
    n = len(parts)
    
    first = parts[0].strip()
    last = parts[-1].strip() if n > 1 else ""
    
    if n == 1:
        return first if len(first) <= 18 else first[:14].strip()
    if n == 2:
        return f"{first[:14].strip()} - {last[:10].strip()}"
    return f"{first[:14].strip()} - ... - {last[:10].strip()}"


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
                "Number_of_Incidents" : "Number of Incidents"}
        )
        fig.update_layout(
            font=dict(size=14),
            legend_title_text='', 
            title={'text': f"Events by Month <br> Grouped by Level of Injury in {entered_year} \n",
                'x': 0.5, 'y': 0.97, 'pad':{'t':30, 'b':10},                                                                             # Center the title horizontally
                'xanchor': 'center'},                                                                   # Anchor the title to the center
            legend=dict(orientation="h",
            yanchor="top",
            y=1.15,
            xanchor="center",
            x=0.48
            ),
            margin=dict(t=160, r=40, l=70)
        )
        fig.update_traces(hovertemplate=
                            "Level of Injury: %{fullData.name}<br>" +
                            "Month: %{x}<br>" +
                            "Number of Incidents: %{y}<extra></extra>"
        ) 

        fig.update_xaxes(tickangle=-45)

        # Select data based on the entered year
        df_division_peryear = df_peryear[['Division', 'Level_of_Injury']].groupby('Division').count()
        df_division_peryear= df_division_peryear['Level_of_Injury'].sort_values(ascending =False)       # to series
            
            
        fig1 = px.bar(df_division_peryear, x =df_division_peryear.index, y = df_division_peryear.values,
                                template = 'plotly_dark',
                                text = df_division_peryear.values,
                                labels={"y" : 'Number of Incidents'}
        )     
        fig1.update_traces(textposition='outside',
                           hovertemplate=
                            "Division: %{x}<br>" +
                            "Number of Incidents: %{y}<extra></extra>"
        ) 

        fig1.update_layout( font=dict(size=14),
            title={
                'text': f"Events by Divison in {entered_year}",
                'x': 0.5,                                                                               # Center the title horizontally
                'xanchor': 'center'                                                                     # Anchor the title to the center
            },
            margin=dict(t=98, r=40, l=70)
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

        pivot_Top10N_df_peryear['ShortLabel'] = pivot_Top10N_df_peryear['Neighbourhood'].apply(shorten_neighbourhood)
        pivot_Top10N_df_peryear['FullLabel'] = pivot_Top10N_df_peryear['Neighbourhood']
        pivot_Top10N_df_peryear = pivot_Top10N_df_peryear.fillna(0)
        pivot_Top10N_df_melted = pivot_Top10N_df_peryear.melt(id_vars=['Neighbourhood', 'ShortLabel', 'FullLabel'], var_name='Level_of_Injury', value_name='Number_of_Incidents')
        fig2 = px.bar(pivot_Top10N_df_melted, x ='ShortLabel' , y='Number_of_Incidents', color = 'Level_of_Injury',
            template = 'plotly_dark',
            labels={'Number_of_Incidents' : 'Number of Incidents', 'ShortLabel':'Neighbourhood'},          
            hover_data={
                'FullLabel': True,
                'ShortLabel': False
            }
        )
        fig2.update_layout(
            font=dict(size=14),
            legend_title_text='',
            title={'text': f"Events by Neighbourhood <br> Grouped by Level of Injury in {entered_year}",
                'x': 0.5,'y': 0.97, 'pad':{'t':30, 'b':10},                                                  # Center the title horizontally
                'xanchor': 'center'                                         # Anchor the title to the center
            },
            legend=dict(orientation="h",
            yanchor="top",
            y=1.17,
            xanchor="center",
            x=0.5
            ),
            margin=dict(t=160, r=40, l=170)
        )
        fig2.update_xaxes(
            tickvals=pivot_Top10N_df_melted['ShortLabel'],
            tickangle=-45
        )
        fig2.update_traces(
            customdata=pivot_Top10N_df_melted[['FullLabel']].values,
            hovertemplate=
                "Level of Injury: %{fullData.name}<br>" +        #fullData.name returns the name of the trace (i.e., the color label, "Level_of_Injury")   
                "Number of Incidents: %{y}<br>" +
                "Neighbourhood: %{customdata[0]} <extra></extra>"
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
        pivot_Top10Wards_peryear_df[['WardNum', 'WardName']] = (pivot_Top10Wards_peryear_df['Ward'].str.replace('Ward ', '', regex=False).str.split(' - ', expand=True))
        pivot_Top10Wards_peryear_df['MultiIndexLabel'] =('Ward ' + pivot_Top10Wards_peryear_df['WardNum'] + ' - ' + pivot_Top10Wards_peryear_df['WardName'] + ',<br>' + pivot_Top10Wards_peryear_df['Councillor'])
        pivot_Top10Wards_peryear_df['ShortLabel'] = (
            'Ward ' + pivot_Top10Wards_peryear_df['WardNum'] + ', ' +
            pivot_Top10Wards_peryear_df['Councillor'].apply(
                lambda x: f"{x.split()[0][0]}. {x.split()[-1]}" if isinstance(x, str) and len(x.split()) > 1 else x
            )
        )
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.drop(columns=['Councillor', 'Ward','WardName', 'WardNum'])
        pivot_Top10Wards_peryear_df = pivot_Top10Wards_peryear_df.fillna(0)
        pivot_Top10Wards_peryear_df_melted = pivot_Top10Wards_peryear_df.melt(id_vars=['ShortLabel','MultiIndexLabel' ], var_name='Level_of_Injury', value_name='Number_of_Incidents')
        fig3 = px.bar(pivot_Top10Wards_peryear_df_melted, x ='ShortLabel', y ='Number_of_Incidents', color = 'Level_of_Injury',
            template = 'plotly_dark',
            labels={'Number_of_Incidents': 'Number of Incidents', 'ShortLabel':'MultiIndexLabel - Ward, Councillor'},
            hover_data={
                'MultiIndexLabel': True,   # show full name
                'ShortLabel': False,  # hide short label in hover
            }
        )
                    
        fig3.update_layout(font=dict(size=14),
            legend_title_text='',
            #hoverlabel= {'font_size': 20},
            title={'text': f"Events by Ward and Councillor <br> Grouped by Level of Injury in {entered_year}",
                'x': 0.5, 'y': 0.97, 'pad':{'t':30, 'b':10},                                                                              # Center the title horizontally
                'xanchor': 'center'                                                                     # Anchor the title to the center
            },
            legend=dict(orientation="h",
            yanchor="top",
            y=1.18,
            xanchor="center",
            x=0.48
            ), 
            margin=dict(t=160, r=40, l=70)                                                                             # Adjust height as needed
        )

        fig3.update_xaxes(
            tickvals=pivot_Top10Wards_peryear_df_melted['ShortLabel'],
            tickangle=-45
        )

        fig3.update_traces(
            customdata=pivot_Top10Wards_peryear_df_melted[['MultiIndexLabel']].values,
            hovertemplate=
                "Level of Injury: %{fullData.name}<br>" +        #fullData.name returns the name of the trace (i.e., the color label, "Level_of_Injury")   
                "Number of Incidents: %{y}<br>" +
                "Ward, Councillor: %{customdata[0]} <extra></extra>"
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
            zoom=8.1
        )  

        fig4.update_traces(
            marker = {'size':8, 'color':'red'},
            hovertemplate= "<b>%{hovertext}</b><br><br>" +                                             
                "<b>%{customdata[0]}</b><br>" + 
                "Councillor: %{customdata[1]}<br>"  +
                "Level of Injury: %{customdata[2]}<br>",   
            customdata=df_peryear[['Ward','Councillor', 'Level_of_Injury' ]].values,
            hovertext=df_peryear['Neighbourhood'],
        )
        fig4.update_layout(
            title={'text': f"Event Coordinates for {entered_year} Shootings", 'x': 0.5,
            },
            map_layers=[{
                'sourcetype': 'geojson',
                'source': ward_layer1,                                      # GeoJSON data loaded from the URL
                'type': 'line',                                             # Use 'line' to show ward boundaries
                'color': 'black',                                           # Color of the lines
                'line': {'width': 1.5}                                      # Width of the boundary lines
            }], margin=dict(t=110, r=20, l=20)
        ) 
        return [
            dbc.Row([
                dbc.Col(dcc.Graph( figure=fig), 
                        xs=12, sm=12, md=12, lg=6, xl=6,
                        className="chart-height2"
                ),
                dbc.Col(dcc.Graph( figure=fig1), 
                        xs=12, sm=12, md=12, lg=6, xl=6,
                        className="chart-height2"
                )
            ], className=" mb-4 g-4"),
            dbc.Row([
                dbc.Col(dcc.Graph( figure=fig2),
                        xs=12, sm=12, md=12, lg=6, xl=6,
                        className="chart-height2"
                ),
                dbc.Col(dcc.Graph( figure=fig3), 
                        xs=12, sm=12, md=12, lg=6, xl=6,
                        className="chart-height2"
                ) 
            ], className="mb-4 g-4 "),
            dbc.Row([
                dbc.Col(dcc.Graph( figure=fig4), 
                        xs=12, sm=12, md=12, lg=12, xl=12,
                )
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
                title='Events by Level of Injury',
                labels={"Level_of_Injury": "Level of Injury", "y" : "Number of Incidents"}
            )
            fig10.update_traces(textposition='outside',
                                hovertemplate=
                                        "Level of Injury: %{x}<br>" +       
                                        "Number of Incidents: %{y}<extra></extra>"
            )
            fig10.update_layout(
                      font=dict(size=14),
                      title={
                          'xanchor': 'center',
                          'x': 0.5, 
                          #'y': 0.97, 'pad':{'t':30, 'b':10}
                      },   
                margin=dict(r=40, l=70)
            )

            fig10.update_xaxes(tickangle=-45)

            # Time of day - Overall
            df_ToD = df['Time_of_Day'].value_counts()
            df_ToD = df_ToD.to_frame('Number of Incidents') 
            fig11 = px.pie(df_ToD, values ='Number of Incidents', names =df_ToD.index, hole=.25,
                template = 'plotly_dark',
                color = df_ToD.index,
                color_discrete_map = {df_ToD.index[0]: 'red', df_ToD.index[1]:'orange', df_ToD.index[2]:'green', df_ToD.index[3]: 'blue'},
                labels={"index" : 'Time of Day'},
                title= 'Events by Time of day'
                )
            fig11.update_layout(title_x = 0.5, title_y = 0.95, font=dict(size=14),
                legend=dict(orientation="h",
                yanchor="top",
                y=1.15,
                xanchor="center",
                x=0.5
                ),
                margin=dict(t=160),
                #height=1000  # Adjust height as needed
            )
            fig11.update_traces(hovertemplate=
                                "Time of Day: %{label}<br>" +       
                                "Number of Incidents: %{value}<extra></extra>"
            )

            # Division - Overall
            df_division = df[['Division', 'Level_of_Injury']].groupby('Division').count()
            df_division = df_division['Level_of_Injury'].sort_values(ascending =False) # to series
            df_division = df_division.to_frame().reset_index()
            fig12 = px.bar(df_division, x ='Division', y = 'Level_of_Injury', 
                template = 'plotly_dark',
                text = 'Level_of_Injury',
                labels={"Level_of_Injury" : 'Number of Incidents'},
                title= 'Events by Divison'
            )
            fig12.update_traces(textposition='outside',
                                hovertemplate=
                                    "Division: %{x}<br>" +       
                                    "Number of Incidents: %{y}<extra></extra>"
            )
                                

            fig12.update_layout(title_x= 0.5, font=dict(size=14),
                                margin=dict(r=40, l=70)
        
            )     

            # Years - Overall
            df_years = df[['Occurred_Year', 'Level_of_Injury', 'ID']].groupby(['Occurred_Year','Level_of_Injury']).count()
            df_years= df_years.reset_index()
            pivot_df = df_years.pivot(index='Occurred_Year', columns='Level_of_Injury', values='ID')
            pivot_df = pivot_df.reset_index()
            pivot_df_melted = pivot_df.melt(id_vars='Occurred_Year', var_name='Level_of_Injury', value_name='Number_of_Incidents')
            
            pivot_df_melted['Level_of_Injury'] = pd.Categorical(pivot_df_melted['Level_of_Injury'],
                categories=values,
                ordered = True
            )
            
            fig13 = px.bar(pivot_df_melted, x ='Occurred_Year', y = 'Number_of_Incidents',
                template = 'plotly_dark',
                color = 'Level_of_Injury',
                color_discrete_map = legend_colors,
                category_orders={'Level_of_Injury': values},
                labels={'Number_of_Incidents' : 'Number of Incidents', 'Occurred_Year':'Year'},
            )
            fig13.update_layout(legend_title_text='', font=dict(size=14), 
                title={'text': 'Events by Year',
                'x': 0.5,  # Center the title horizontally
                'y': 0.97,
                'pad':{'t':30, 'b':10}, 
                'xanchor': 'center'  # Anchor the title to the center         
                },
                legend=dict(orientation="h",
                yanchor="top",
                y=1.15,
                xanchor="center",
                x=0.5
                ),
                margin=dict(t=160, r=40, l=70)
            )

            fig13.update_traces(
                hovertemplate=
                    "Level of Injury: %{fullData.name}<br>" +        #fullData.name returns the name of the trace (i.e., the color label, "Level_of_Injury")   
                    "Year: %{x}<br>" +
                    "Number of Incidents: %{y}<extra></extra>"
            ) 
            
                    
            return [
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig10), 
                            xs=12, sm=12, md=12, lg=6, xl=6,
                            className="chart-height2"
                    ),
                    dbc.Col(dcc.Graph(figure=fig11), 
                            xs=12, sm=12, md=12, lg=6, xl=6,
                            className="chart-height2"
                    )
                ], className="mb-4 g-4"),
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig12),
                            xs=12, sm=12, md=12, lg=6, xl=6,
                            className="chart-height2"
                    ),
                    dbc.Col(dcc.Graph(figure=fig13), 
                            xs=12, sm=12, md=12, lg=6, xl=6,
                            className="chart-height2"
                    )
                ], className="mb-4 g-4"),
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
    
    pivot_Top10N_LoI_df['ShortLabel'] = pivot_Top10N_LoI_df['Neighbourhood'].apply(shorten_neighbourhood)
    pivot_Top10N_LoI_df['FullLabel'] = pivot_Top10N_LoI_df['Neighbourhood']
    
    pivot_Top10N_LoI_df = pivot_Top10N_LoI_df.fillna(0)

    pivot_Top10N_LoI_df_melted = pivot_Top10N_LoI_df.melt(id_vars=['Neighbourhood', 'ShortLabel', 'FullLabel'], var_name='Level_of_Injury', value_name='Number_of_Incidents')
    
    pivot_Top10N_LoI_df_melted['Level_of_Injury'] = pd.Categorical(pivot_Top10N_LoI_df_melted['Level_of_Injury'],
        categories=values,
        ordered = True
    )

    fig5 = px.bar(pivot_Top10N_LoI_df_melted, x ='ShortLabel', y = 'Number_of_Incidents',
        template = 'plotly_dark',
        color = 'Level_of_Injury',
        color_discrete_map = legend_colors, 
        labels={"Number_of_Incidents" : 'Number of Incidents', 'ShortLabel':'Neighbourhood'},
        hover_data={
            'FullLabel': True,
            'ShortLabel': False
        },
        category_orders={'Level_of_Injury': values} 
        )
                    
    fig5.update_layout(
        font=dict(size=14),
        title_x= 0.5, 
        title={'text': f'{title_text} <br> Events by Neighbourhood',
            'x': 0.5, 'y': 0.93,                                                                               # Center the title horizontally
            'xanchor': 'center'},                                                                    # Anchor the title to the center}
        margin=dict(t=120, r=40, l=70 ),
        showlegend=False
    )
    fig5.update_xaxes(
            tickvals=pivot_Top10N_LoI_df_melted['ShortLabel'],
            #ticktext=[label.replace(" - ", "<br>") for label in pivot_Top10N_LoI_df_melted['Neighbourhood']],
            tickangle=-45
    )
    
    fig5.update_traces(
            customdata=pivot_Top10N_LoI_df_melted[['FullLabel']].values,
            hovertemplate=
                "Level of Injury: %{fullData.name}<br>" +        #fullData.name returns the name of the trace (i.e., the color label, "Level_of_Injury")   
                "Number of Incidents: %{y}<br>" +
                "Neighbourhood: %{customdata[0]} <extra></extra>"
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

    pivot_Top10Wards_LoI_df[['WardNum', 'WardName']] = (pivot_Top10Wards_LoI_df['Ward'].str.replace('Ward ', '', regex=False).str.split(' - ', expand=True))

    pivot_Top10Wards_LoI_df['MultiIndexLabel'] =('Ward ' + pivot_Top10Wards_LoI_df['WardNum'] + ' - ' + pivot_Top10Wards_LoI_df['WardName'] + ',<br>' + pivot_Top10Wards_LoI_df['Councillor'])

    pivot_Top10Wards_LoI_df['ShortLabel'] = (
            'Ward ' + pivot_Top10Wards_LoI_df['WardNum'] + ', ' +
            pivot_Top10Wards_LoI_df['Councillor'].apply(
                lambda x: f"{x.split()[0][0]}. {x.split()[-1]}" if isinstance(x, str) and len(x.split()) > 1 else x
            )
        )

    pivot_Top10Wards_LoI_df = pivot_Top10Wards_LoI_df.drop(columns=['Councillor','Ward', 'WardName', 'WardNum'])
    
    pivot_Top10Wards_LoI_df=pivot_Top10Wards_LoI_df.fillna(0)
    
    pivot_Top10Wards_LoI_melted = pivot_Top10Wards_LoI_df.melt(id_vars=['ShortLabel', 'MultiIndexLabel'], var_name='Level_of_Injury', value_name='Number_of_Incidents')

    fig6 = px.bar(pivot_Top10Wards_LoI_melted, x ='ShortLabel', y ='Number_of_Incidents',
        template = 'plotly_dark',
        color = 'Level_of_Injury',
        color_discrete_map = legend_colors,
        labels={"Number_of_Incidents" : 'Number of Incidents', 'ShortLabel':'MultiIndexLabel - Ward, Councillor'},
        hover_data={
                'MultiIndexLabel': True,   # show full name
                'ShortLabel': False,  # hide short label in hover
        }
    )

    fig6.update_layout(
        font=dict(size=14),  
        title={'text': f'{title_text} <br> Events by Ward and Councillor ',
            'x': 0.5, 'y':0.93,                                                                               # Center the title horizontally
            'xanchor': 'center'},                                                                   # Anchor the title to the center
        margin=dict(t=120, r=40, l=70 ),
        showlegend=False)
    
    fig6.update_xaxes(
            tickvals=pivot_Top10Wards_LoI_melted['ShortLabel'],
            tickangle=-45
    )

    fig6.update_traces(
            customdata=pivot_Top10Wards_LoI_melted[['MultiIndexLabel']].values,
            hovertemplate=
                "Level of Injury: %{fullData.name}<br>" +        #fullData.name returns the name of the trace (i.e., the color label, "Level_of_Injury")   
                "Number of Incidents: %{y}<br>" +
                "Ward, Councillor: %{customdata[0]} <extra></extra>"
    ) 

    
    # Years - LoI
    df_years_LoI = df_LoI[['Occurred_Year', 'Level_of_Injury', 'ID']].groupby(['Occurred_Year','Level_of_Injury']).count()
    df_years_LoI= df_years_LoI.reset_index()
    pivot_df_LoI = df_years_LoI.pivot(index='Occurred_Year', columns='Level_of_Injury', values='ID')
    pivot_df_LoI = pivot_df_LoI.reset_index()
    pivot_df_LoI_melted = pivot_df_LoI.melt(id_vars='Occurred_Year', var_name='Level_of_Injury', value_name='Number_of_Incidents')
    
    pivot_df_LoI_melted['Level_of_Injury'] = pd.Categorical(pivot_df_LoI_melted['Level_of_Injury'],
        categories=values,
        ordered = True
    )

    fig7 = px.bar(pivot_df_LoI_melted, x ='Occurred_Year', y = 'Number_of_Incidents', 
        template = 'plotly_dark',
        color = 'Level_of_Injury',
        color_discrete_map = legend_colors,
        category_orders={'Level_of_Injury': values},
        labels={"Number_of_Incidents" : 'Number of Incidents', 'Occurred_Year':'Year'},                                 
    )
    fig7.update_layout( showlegend=False, font=dict(size=14),
        title={'text': f'{title_text} <br> Events by Year ',
            'x': 0.5, 'y': 0.93,                                                                              
            'xanchor': 'center'},
            margin=dict(t=120, r=40, l=70 )
    )

    fig7.update_traces(
                hovertemplate=
                    "Level of Injury: %{fullData.name}<br>" +        #fullData.name returns the name of the trace (i.e., the color label, "Level_of_Injury")   
                    "Year: %{x}<br>" +
                    "Number of Incidents: %{y}<extra></extra>"
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
        labels={"Number_of_Incidents" : 'Number of Incidents', 'Occurred_Month':'Month'},
         
    )
    fig8.update_layout(
        font=dict(size=14),
        showlegend=False,
        title={'text': f"{title_text} <br> Events by Month",
            'x': 0.5,  'y': 0.93,                                                                               # Center the title horizontally
            'xanchor': 'center'                                                                     # Anchor the title to the center
        },
        margin=dict(t=120, r=40, l=70),
    )

    fig8.update_traces(hovertemplate=
                            "Level of Injury: %{fullData.name}<br>" +
                            "Month: %{x}<br>" +
                            "Number of Incidents: %{y}<extra></extra>"
    ) 
    fig8.update_xaxes(tickangle=-45)

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
        zoom=8.1
    )
    fig9.update_traces(
    marker = {'size':8, 'color':'red'},
    hovertemplate=  "<b>%{hovertext}</b><br><br>" +  # Country Name
        "<b>%{customdata[0]}</b><br>" + 
        "Councillor: %{customdata[1]}<br>"  +
        "Level of Injury: %{customdata[2]}<br>" + 
        "%{customdata[3]}<br>",  
    customdata=df_LoI[['Ward','Councillor', 'Level_of_Injury', 'Occurred_Year' ]].values,
    hovertext=df_LoI['Neighbourhood'],
    )

    fig9.update_layout(
        title={'text': f"Event Coordinates for <br> {title_text} <br> Shootings",
                'x': 0.5,  # Center the title horizontally
                'pad': {'b': 50}  
        },
        map_layers=[{
            'sourcetype': 'geojson',
            'source': ward_layer1,  # GeoJSON data loaded from the URL
            'type': 'line',        # Use 'line' to show ward boundaries
            'color': 'black',       # Color of the lines
            'line': {'width': 1.5}   # Width of the boundary lines
        }], margin=dict(t=150, r=20, l=20)
    )

    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig5),
                    xs=12, sm=12, md=12, lg=6, xl=6,
                    className="chart-height2"
            ),
            dbc.Col(dcc.Graph(figure=fig6),
                    xs=12, sm=12, md=12, lg=6, xl=6,
                    className="chart-height2" 
            )
        ], className="mb-4 g-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig7),
                    xs=12, sm=12, md=12, lg=6, xl=6,
                    className="chart-height2"
            ),
            dbc.Col(dcc.Graph(figure=fig8), 
                    xs=12, sm=12, md=12, lg=6, xl=6,
                    className="chart-height2"
            )
        ], className="mb-4 g-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig9),
                    xs=12, sm=12, md=12, lg=12, xl=12,
            )
        ], className="mapcharts")
    ]
# else:
#     return None
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------    
    
 
