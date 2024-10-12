import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd

from scripts.baseDataCreation import create_base_df, create_daily_df
from scripts.espnQuery import espn_fantasy_pull, espn_team_pull
from scripts.calculateOptimalTeam import calculate_optimal_team
from app import app


df = create_base_df(season_year=2024)
#df['salary'] = df['2023-24']
player_list = espn_fantasy_pull(year = 2024, leagueid=1661951033)
team_dict = espn_team_pull(year = 2024, leagueid=1661951033)
team_list = list(team_dict.keys())


def normalize(array):
    return np.asarray([float(i)/np.max(array) for i in array])

layout = html.Div([
    html.H3('Team Optimizer'),
    # html.Div([
    #     html.Div(
    #         dcc.Link('Go to player table', href='/'),
    #         style={'display': 'inline-block', 'width': '20%'}
    #     ),
    #     html.Div(
    #         dcc.Link('Go to salary calculator', href='/salaryCalculator'),
    #         style={'display': 'inline-block', 'width': '20%'}
    #     ),
    #     html.Div(
    #         dcc.Link('Go to team analysis tool', href='/teamAnalysis'),
    #         style={'display': 'inline-block', 'width': '20%'}
    #     )
    # ]),
    # html.Br(),

    dbc.Nav([
        dbc.NavItem(dbc.NavLink('Go to player table', href='/')),
        dbc.NavItem(dbc.NavLink('Go to salary calculator', href='/salaryCalculator')),
        dbc.NavItem(dbc.NavLink('Go to team analysis tool', href='/teamAnalysis'))
    ], horizontal='center'),
    html.Br(),
    dcc.Checklist(
        id='checklist-options',
        options=[
            {'label': 'FG%', 'value': 'field_goal_percentage'},
            {'label': 'FT%', 'value': 'free_throw_percentage'},
            {'label': '3PM', 'value': 'made_three_point_field_goals'},
            {'label': 'Reb', 'value': 'rebounds'},
            {'label': 'Ast', 'value': 'assists'},
            {'label': 'Stl', 'value': 'steals'},
            {'label': 'Blk', 'value': 'blocks'},
            {'label': 'TO', 'value': 'turnovers'},
            {'label': 'ppg', 'value': 'ppg'}
        ],
        value=[
            'field_goal_percentage', 'free_throw_percentage', 'made_three_point_field_goals',
            'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'ppg'
        ],
        labelStyle={'display': 'inline-block', 'width': '11%'}
    ),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='fg-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='ft-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='3p-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='reb-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='ast-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='stl-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='blk-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='to-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='ppg-weighting',
                options=[
                    {'label': '0.5x', 'value': '0.5x'},
                    {'label': '1x', 'value': '1x'},
                    {'label': '1.5x', 'value': '1.5x'},
                    {'label': '2x', 'value': '2x'}
                ],
                value='1x'
            ),
            style={'display': 'inline-block', 'width': '11%'}
        )
    ]),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='inclusion-list-dropdown',
                options=[{'label': str(name), 'value': str(name)} for name in df['no_accents']],
                placeholder="Select players you wish to include in your team calculation.",
                multi=True
            ),
            style={'width': '48%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='exclusion-list-dropdown',
                options=[{'label': str(name), 'value': str(name)} for name in df['no_accents']],
                placeholder='Select players you wish to exclude in your team calculation.',
                multi=True
            ),
            style={'width': '48%'}
        )
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        html.Div(
            dcc.Checklist(
                id='fantasy-league-checklist',
                options=[
                    {'label': 'Exclude players in my fantasy league', 'value': 'fantasy_exclusion'}
                ],
                value=[
                    'fantasy_exclusion'
                ]
            )
        ),
        html.Div(
            dcc.Dropdown(
                id='espn-team-name',
                options=[{'label': str(team), 'value': str(team)} for team in team_list],
                placeholder='Fantasy Team'
            ),
            style={'width': '20%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='last-n-days',
                options=[
                    {'label': 'Last 7 Days', 'value': '7'},
                    {'label': 'Last 15 Days', 'value': '15'},
                    {'label': 'Last 30 Days', 'value': '30'}
                ],
                placeholder='Past Days Filter'
            ),
            style={'width': '20%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='number-players-dropdown',
                options=[
                    {'label': '10', 'value': '10'},
                    {'label': '11', 'value': '11'},
                    {'label': '12', 'value': '12'},
                    {'label': '13', 'value': '13'}
                ],
                placeholder='How many players on your team?'
            ),
            style={'width': '30%'}
        )
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Br(),
    html.Div([
        dbc.Button('Calculate', id='calculation-button', color='success'),
        dbc.Button('Reset', id='reset-button', color='warning')
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Br(),
    html.Div([
        dcc.Loading(
            id='loading-2',
            children=html.Div(
                id='intermediate-value',
                style={'display': 'none'}
            ),
            type='dot',
            color='#56cc9d'
        )
    ]),
    html.Div([
        dcc.Loading(
            id='loading-1',
            children=html.Div(
                id='solutions-table',
                className='tableDiv'
            ),
            type='circle',
            color='#56cc9d'
        )
    ]),
    html.Br(),
    html.Div(
        id='current-score',
        style={'display': 'none'}
    ),
    html.Div(
        id='projected-score',
        style={'display': 'none'}
    ),
    html.Div(
        id='comparison-text'
    )
])

@app.callback(
    Output('calculation-button', 'n_clicks'),
    [Input('reset-button', 'n_clicks')])
def update(reset):
    return 0

@app.callback(
    Output('intermediate-value', 'children'),
    [Input('last-n-days', 'value')])
def call_hidden_data(last_n_days):
    if last_n_days is not None:
        print('Querying hidden data')
        hidden_df = create_daily_df(last_days=int(last_n_days))
        return hidden_df.to_json(orient='split')

@app.callback(
    [Output('solutions-table', 'children'),
     Output('current-score', 'children'),
     Output('projected-score', 'children')],
    [Input('fg-weighting', 'value'),
     Input('ft-weighting', 'value'),
     Input('3p-weighting', 'value'),
     Input('reb-weighting', 'value'),
     Input('ast-weighting', 'value'),
     Input('stl-weighting', 'value'),
     Input('blk-weighting', 'value'),
     Input('to-weighting', 'value'),
     Input('ppg-weighting', 'value'),
     Input('checklist-options', 'value'),
     Input('fantasy-league-checklist', 'value'),
     Input('number-players-dropdown', 'value'),
     Input('exclusion-list-dropdown', 'value'),
     Input('inclusion-list-dropdown', 'value'),
     Input('espn-team-name', 'value'),
     Input('calculation-button', 'n_clicks'),
     Input('intermediate-value', 'children')])
def create_solution_table(fg_value, ft_value, three_point_value, rebs, asts, stls, blks,
    tos, ppg, checklist_options, fleague, number_players, exclusion_list, inclusion_list,
    fantasy_team, calculation_clicks, last_n_days_data):
    print(calculation_clicks)
    print(last_n_days_data)
    if exclusion_list is None:
        exclusion_list = []
    if inclusion_list is None:
        inclusion_list = []
    if fleague:
        fantasy_players = espn_fantasy_pull(year = 2024, leagueid=1661951033)
        if fantasy_team:
            exclusion_list += list(set(fantasy_players) - set(team_dict[fantasy_team]))
        else:
            exclusion_list += fantasy_players
    weight_dict = {
        'field_goal_percentage': float(fg_value[:-1]),
        'free_throw_percentage': float(ft_value[:-1]),
        'made_three_point_field_goals': float(three_point_value[:-1]),
        'rebounds': float(rebs[:-1]),
        'assists': float(asts[:-1]),
        'steals': float(stls[:-1]),
        'blocks': float(blks[:-1]),
        'turnovers': float(tos[:-1]),
        'ppg': float(ppg[:-1])
    }

    temp_table_col_list = ['name', 'positions', 'field_goal_percentage', 'free_throw_percentage', 'made_three_point_field_goals',
        'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'ppg', 'salary', 'avg_fantasy_pts']
    temp_table_cols = [{'name': i, 'id': i} for i in temp_table_col_list]

    if (calculation_clicks is None) or (number_players is None):
        print('None')
        raise PreventUpdate
    elif calculation_clicks == 0:
        print('0')
        return html.Div([
            dt.DataTable(
                id='optimal-results-table',
                data=[]
            )
        ]), html.Br(), html.Br()
    else:
        if last_n_days_data is None:
            temp_table = df
        else:
            print("Reading hidden data")
            temp_table = pd.read_json(last_n_days_data, orient='split')
        temp_table.loc[temp_table['attempted_field_goals'] <= np.percentile(temp_table['attempted_field_goals'], 25), ['field_goal_percentage']] = 0
        temp_table.loc[temp_table['attempted_free_throws'] <= np.percentile(temp_table['attempted_free_throws'], 25), ['free_throw_percentage']] = 0
        temp_table['ppg'] = temp_table.ppg.round(1)
        # temp_table['raw_score'] = 0

        # for option in checklist_options:
        #     if option == 'turnovers':
        #         temp_table['raw_score'] -= normalize(temp_table[option])*weight_dict[option]
        #     else:
        #         temp_table['raw_score'] += normalize(temp_table[option])*weight_dict[option]
        scores = temp_table['avg_fantasy_pts'].to_numpy()
        sals = temp_table['2024-25'].replace('[\$,]', '', regex=True).astype(float).to_numpy()
        names = temp_table['no_accents'].to_numpy()
        # Wemby 1878, ja 1659, rest 2000
        optimal_team = calculate_optimal_team(slots=int(number_players), max_cost=2300,
            exclusion_list=exclusion_list, inclusion_list=list(set(inclusion_list) - set(exclusion_list)),
            scores=scores, sals=sals, names=names)
        optimal_team_table = temp_table[temp_table['no_accents'].isin(optimal_team)]
        # while len(set(['C', 'PF', 'SF', 'PG', 'SG']) - set(optimal_team_table['positions'].tolist())) > 0:
        #     # Recalculate to get all positions
        #     player_to_exclude = optimal_team_table.loc[optimal_team_table['raw_score'] == optimal_team_table['raw_score'].min()]['no_accents'].tolist()
        #     exclusion_list += player_to_exclude
        #     exclusion_list = list(set(exclusion_list))
        #     print("Cant find all positions, excluding "+player_to_exclude[0])
        #     print("Running optimal team again...")
        #     optimal_team = calculate_optimal_team(slots=int(number_players), max_cost=1450,
        #         exclusion_list=exclusion_list, inclusion_list=list(set(inclusion_list) - set(exclusion_list)),
        #         scores=scores, sals=sals, names=names)
        #     optimal_team_table = temp_table[temp_table['no_accents'].isin(optimal_team)]
        optimal_team_table = optimal_team_table.rename(columns={"2024-25": "salary"})
        optimal_team_table = optimal_team_table[['name', 'positions', 'field_goal_percentage', 'free_throw_percentage', 'made_three_point_field_goals',
            'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'ppg', 'salary', 'avg_fantasy_pts']]
        optimal_team_table['avg_fantasy_pts'] = optimal_team_table['avg_fantasy_pts'].round(2)
        optimal_team_table= optimal_team_table.sort_values(by=['avg_fantasy_pts'], ascending=False)
        top_n_score = (optimal_team_table.nlargest(10, 'avg_fantasy_pts'))['avg_fantasy_pts'].sum()
        total_row = pd.DataFrame([[
            'Total',
            '',
            round(optimal_team_table['field_goal_percentage'].mean(),1),
            round(optimal_team_table['free_throw_percentage'].mean(),1),
            optimal_team_table['made_three_point_field_goals'].sum(),
            optimal_team_table['rebounds'].sum(),
            optimal_team_table['assists'].sum(),
            optimal_team_table['steals'].sum(),
            optimal_team_table['blocks'].sum(),
            optimal_team_table['turnovers'].sum(),
            round(optimal_team_table['ppg'].mean(),1),
            '${:,.2f}'.format(optimal_team_table['salary'].str[1:].str.replace(",", "").astype(float).sum()),
            round(optimal_team_table['avg_fantasy_pts'].sum(),2)
        ]],
        columns = [
            'name', 'positions', 'field_goal_percentage', 'free_throw_percentage', 'made_three_point_field_goals',
                'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'ppg', 'salary', 'avg_fantasy_pts'
        ])
        optimal_team_table = pd.concat([optimal_team_table, total_row])
        return html.Div([
            dt.DataTable(
                id='optimal-results-table',
                columns=temp_table_cols,
                data=optimal_team_table.to_dict('rows'),
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{name} eq "Total"',
                        },
                        'backgroundColor': 'LightGray'
                    }
                ]
            )
        ]), temp_table.to_json(orient='split'), top_n_score

@app.callback(
    Output('comparison-text', 'children'),
    [Input('solutions-table', 'children'),
     Input('current-score', 'children'),
     Input('projected-score', 'children'),
     Input('espn-team-name', 'value'),
     Input('calculation-button', 'n_clicks')])
def write_comparison_text(solutions_table, current_score, projected_score, fantasy_team, calculation_clicks):
    if calculation_clicks == 0:
        return ""
    elif solutions_table and (current_score is not None):
        print(current_score)
        current_score_df = pd.read_json(current_score, orient='split')
        current_roster = current_score_df.loc[current_score_df['no_accents'].isin(team_dict[fantasy_team]), 'avg_fantasy_pts']
        raw_score = round((current_roster.nlargest(10)).sum(), 2)
        return "Your team's projected raw score is " + str(round(projected_score, 2)) + \
            ". Your team's current raw score is " + str(raw_score)
