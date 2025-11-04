from dash import Dash, dcc, html, page_registry, page_container, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, 
           external_stylesheets= [dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}], #maximum-scale = 1.2, minimum-scale=1.0'
           use_pages=True)
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>My Dash App</title>

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-2EL6EN1XKF"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-2EL6EN1XKF', {'send_page_view': false});
    </script>

    {%metas%}
    {%favicon%}
    {%css%}
  </head>
  <body>
    {%app_entry%}
    <footer>
      {%config%}
      {%scripts%}
      {%renderer%}
    </footer>
  </body>
</html>
'''

# define navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overall Stats", href="/", external_link=True, active="exact", class_name="main-navbar")),
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
    footer,
    html.Div(id="analytics")
])

@app.callback(
    Output("analytics", "children"),
    Input("url", "pathname")
)
def track_pageview(pathname):
    return html.Script(f"gtag('event', 'page_view', {{'page_path': '{pathname}'}});")

if __name__ == '__main__':
    app.run() #debug=True
