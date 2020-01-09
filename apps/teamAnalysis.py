import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash
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
            style={'width': '30%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='last-n-days',
                options=[
                    {'label': 'Last 7 Days', 'value': '7'},
                    {'label': 'Last 15 Days', 'value': '15'},
                    {'label': 'Last 30 Days', 'value': '30'},
                    {'label': 'Entire Season', 'value': 'season'}
                ],
                value='season'
            ),
            style={'width': '30%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='opposing-team',
                options=[{'label': str(team), 'value': str(team)} for team in team_list],
                placeholder='Opposing Team'
            ),
            style={'width': '30%'}
        )
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Loading(
            id='loading-2',
            children=html.Div(
                id='intermediate-value-team-analysis',
                style={'display': 'none'}
            ),
            type='dot'
        )
    ]),
    html.Br(),
    dcc.Graph(
        id='comparison-radar',
        figure = {}
    )
])

@app.callback(
    [Output('your-team', 'options'),
     Output('opposing-team', 'options')],
    [Input('your-team', 'value'),
     Input('opposing-team', 'value')])
def update_dropdowns(value1, value2):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, dash.no_update

    options1 = list(league_analysis_df['team_name'].unique())
    options2 = list(league_analysis_df['team_name'].unique())

    if ctx.triggered[0]['prop_id'] == 'your-team.value':
        temp1, temp2 = options1, options2
        if value1 is not None:
            temp2.remove(value1)
        return [{'label': str(team), 'value': str(team)} for team in temp1], [{'label': str(team), 'value': str(team)} for team in temp2]
    elif ctx.triggered[0]['prop_id'] == 'opposing-team.value':
        temp1, temp2 = options1, options2
        if value2 is not None:
            temp1.remove(value2)
        return [{'label': str(team), 'value': str(team)} for team in temp1], [{'label': str(team), 'value': str(team)} for team in temp2]
    else:
        return dash.no_update, dash.no_update

# Store last n days data as JSON file to make things faster
@app.callback(
    Output('intermediate-value-team-analysis', 'children'),
    [Input('last-n-days', 'value')])
def call_hidden_data(last_n_days_team_analysis):
    if last_n_days_team_analysis == "season":
        hidden_df_team = league_analysis(year=2020, leagueid=22328189)
    else:
        hidden_df_team = league_analysis(year=2020, leagueid=22328189, last_n_days=int(last_n_days_team_analysis))
    return hidden_df_team.to_json(orient='split')

@app.callback(
    Output('comparison-radar', 'figure'),
    [Input('your-team', 'value'),
     Input('opposing-team', 'value'),
     Input('intermediate-value-team-analysis', 'children')])

def generate_radar_chart(your_team, opposing_team, hidden_team_data):
    league_analysis_df = pd.read_json(hidden_team_data, orient='split')
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
