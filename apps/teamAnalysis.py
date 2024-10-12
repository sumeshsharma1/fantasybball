import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash
import plotly.graph_objects as go
import pandas as pd

from scripts.leagueAnalysis import league_analysis
from app import app

# league_analysis_df = league_analysis(year=2020, leagueid=22328189)
# categories = list(league_analysis_df['variable'].unique())
# team_list = list(league_analysis_df['team_name'].unique())

layout = html.Div([
    html.H3('Fantasy Team Analysis'),
    # dcc.Link('Go to player table', href='/'),
    # html.Br(),
    # dcc.Link('Go to salary calculator', href='/salaryCalculator'),
    # html.Br(),
    # dcc.Link('Go to team optimizer', href='/optimalTeam'),
    dbc.Nav([
        dbc.NavItem(dbc.NavLink('Go to player table', href='/')),
        dbc.NavItem(dbc.NavLink('Go to salary calculator', href='/salaryCalculator')),
        dbc.NavItem(dbc.NavLink('Go to team optimizer', href='/optimalTeam'))
    ], horizontal='center'),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='your-team',
                options=[],
                placeholder='Your Team'
            ),
            style={'width': '20%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='league-picker',
                options=[
                    {'label': 'Et Toi, Monsieur Wembanyama?', 'value': '1661951033'},
                    {'label': 'Losses Pool', 'value': '1566531'}
                ],
                value='22328189'
            ),
            style={'width': '20%'}
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
            style={'width': '20%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='opposing-team',
                options=[],
                placeholder='Opposing Team'
            ),
            style={'width': '20%'}
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

# Store last n days data as JSON file to make things faster
@app.callback(
    Output('intermediate-value-team-analysis', 'children'),
    [Input('last-n-days', 'value'),
     Input('league-picker', 'value')])
def call_hidden_data(last_n_days_team_analysis, league_id):
    if last_n_days_team_analysis == "season":
        hidden_df_team = league_analysis(year=2024, leagueid=int(league_id))
    else:
        hidden_df_team = league_analysis(year=2024, leagueid=int(league_id), last_n_days=int(last_n_days_team_analysis))
    return hidden_df_team.to_json(orient='split')

# @app.callback(
#     [Output('your-team', 'options'),
#      Output('opposing-team', 'options')],
#     [Input('intermediate-value-team-analysis', 'children')])
# def create_team_options(hidden_team_data):
#     league_analysis_df = pd.read_json(hidden_team_data, orient='split')
#     options1 = list(league_analysis_df['team_name'].unique())
#     options2 = list(league_analysis_df['team_name'].unique())
#     return [{'label': str(team), 'value': str(team)} for team in options1], [{'label': str(team), 'value': str(team)} for team in options2]

@app.callback(
    [Output('your-team', 'options'),
     Output('opposing-team', 'options')],
    [Input('intermediate-value-team-analysis', 'children'),
     Input('your-team', 'value'),
     Input('opposing-team', 'value')])
def create_team_options(hidden_team_data, value1, value2):
    league_analysis_df = pd.read_json(hidden_team_data, orient='split')
    options1 = list(league_analysis_df['team_name'].unique())
    options2 = list(league_analysis_df['team_name'].unique())

    ctx = dash.callback_context
    print(ctx.triggered[0]['prop_id'])

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
    elif ctx.triggered[0]['prop_id'] == 'intermediate-value-team-analysis.children':
        return [{'label': str(team), 'value': str(team)} for team in options1], [{'label': str(team), 'value': str(team)} for team in options2]
    else:
        return dash.no_update, dash.no_update


@app.callback(
    Output('comparison-radar', 'figure'),
    [Input('your-team', 'value'),
     Input('opposing-team', 'value'),
     Input('intermediate-value-team-analysis', 'children')])

def generate_radar_chart(your_team, opposing_team, hidden_team_data):
    league_analysis_df = pd.read_json(hidden_team_data, orient='split')
    categories = list(league_analysis_df['variable'].unique())
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
