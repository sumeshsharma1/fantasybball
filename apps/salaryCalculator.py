import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd

from scripts.baseDataCreation import create_base_df
from app import app

df = create_base_df(season_year=2020)
df = df.rename(columns={"no_accents": "Player", "2019-20": "Salary"})
df_two_col = df[['Player', 'Salary']]

empty_df = pd.DataFrame(columns=['Player', 'Salary'])

layout = html.Div([
    html.H3('Salary Calculator'),
    # dcc.Link('Go to player table', href='/'),
    # html.Br(),
    # dcc.Link('Go to team optimizer', href='/optimalTeam'),
    # html.Br(),
    # dcc.Link('Go to team analysis tool', href='/teamAnalysis'),
    dbc.Nav([
        dbc.NavItem(dbc.NavLink('Go to player table', href='/')),
        dbc.NavItem(dbc.NavLink('Go to team optimizer', href='/optimalTeam')),
        dbc.NavItem(dbc.NavLink('Go to team analysis tool', href='/teamAnalysis'))
    ], horizontal='center'),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='player-name-dropdown',
                options=[{'label': str(name), 'value': str(name)} for name in df['Player']],
                value='Brook Lopez',
                multi=True
            ),
            style={'width': '40%'}
        ),
        html.Div(
            dt.DataTable(
                id='salary-datatable',
                columns=[{'name': i, 'id': i} for i in empty_df.columns],
                data=[],
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{Player} eq "Total"',
                        },
                        'backgroundColor': 'LightGray'
                    },
                ]
            ),
            style={'width': '40%'}
        )
    ], style={'display': 'flex', 'justify-content': 'space-between'})
])

@app.callback(
    Output('salary-datatable', 'data'),
    [Input('player-name-dropdown', 'value')])

def generate_salary_table(player_name):
    dff = pd.DataFrame(columns=['Player', 'Salary'])
    for player in df['Player']:
        if player in player_name:
            dff = pd.concat([dff, df_two_col[df_two_col['Player'] == player]])


    dff = pd.concat([dff, pd.DataFrame([['Total', '${:,.2f}'.format(dff['Salary'].str[1:].str.replace(",", "").astype(float).sum())]], columns = ['Player', 'Salary'])])
    return(dff.to_dict('records'))
