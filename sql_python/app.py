from dash import Dash, dcc, html, page_registry, page_container
import dash_bootstrap_components as dbc

app = Dash(__name__, 
           external_stylesheets= [dbc.themes.CYBORG],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}], #maximum-scale = 1.2, minimum-scale=1.0'
           use_pages=True)
server = app.server

# define navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Yearly Stats", href="/", external_link=True, active="exact", class_name="main-navbar")),
        dbc.NavItem(dbc.NavLink("Level of Injury Stats", href="/loi_stats_page", active="exact", class_name="main-navbar")),
    ],
    brand="Shootings Ottawa",
    brand_href="https://ottawa-shooting-incidents-data-analysis.onrender.com/",
    color="dark",
    dark=True,
    class_name="main-navbar",
)

# define footer
footer  = dbc.Container(
            dbc.Row(
                [
                    dbc.Col(html.A("Olamide Olayinka | Github", href = 'https://github.com/kodexl'))
                ],
            ),
        className = 'footer text-center',
        fluid = True
)
#define the layout of the app
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    page_container,
    footer
])

if __name__ == '__main__':
    app.run() #debug=True
