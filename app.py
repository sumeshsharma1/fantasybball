import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server
app.title = "Sumesh's Fantasy Basketball Dashboard"
app.config.suppress_callback_exceptions = True
