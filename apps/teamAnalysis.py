import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd

from scripts.leagueAnalysis import league_analysis
from app import app

league_analysis_df = league_analysis(year=2020, leagueid=22328189)
categories = list(league_analysis_df['variable'].unique())
team_list = list(league_analysis_df['team_name'].unique())

layout = html.Div([
    html.H3('Fantasy Team Analysis'),
    dcc.Link('Go to player table', href='/'),
    html.Br(),
    dcc.Link('Go to salary calculator', href='/salaryCalculator'),
    html.Br(),
    dcc.Link('Go to team optimizer', href='/optimalTeam'),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='your-team',
                options=[{'label': str(team), 'value': str(team)} for team in team_list],
                placeholder='Your Team'
            ),
            style={'width': '43%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='opposing-team',
                options=[{'label': str(team), 'value': str(team)} for team in team_list],
                placeholder='Opposing Team'
            ),
            style={'width': '43%'}
        )
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Br(),
    dcc.Graph(
        id='comparison-radar',
        figure = {}
    )
])

@app.callback(
    Output('comparison-radar', 'figure'),
    [Input('your-team', 'value'),
     Input('opposing-team', 'value')])

def generate_radar_chart(your_team, opposing_team):
    fig = go.Figure()
    for team in [your_team, opposing_team]:
        fig.add_trace(go.Scatterpolar(
            r=list(league_analysis_df[league_analysis_df['team_name'] == team]['value']),
            theta=categories,
            fill='toself',
            name=team
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True
    )

    return fig.to_dict()
