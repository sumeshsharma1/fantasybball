import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
from scripts.baseDataCreation import create_base_df
from app import app

total_df_with_salaries = create_base_df(season_year=2020)
#total_df_with_salaries = pd.read_csv('https://raw.githubusercontent.com/sumeshsharma1/fantasybball/master/total_df_with_salaries.csv')
total_df_with_salaries['2019-20'].replace('[\$,]', '', regex=True).astype(float)

def normalize(array):
    return np.asarray([float(i)/np.max(array) for i in array])


layout = html.Div([
    html.H3('Player Data Table'),
    dcc.Link('Go to salary calculator', href='/salaryCalculator'),
    html.Br(),
    dcc.Link('Go to team optimizer', href='/optimalTeam'),
    html.Br(),
    dcc.Link('Go to team analysis tool', href='/teamAnalysis'),
    html.Div([
        html.Div(
            dcc.RangeSlider(
                id='minutes_percentile_slider',
                min=0,
                max=100,
                step=1
            ),
            style={'display': 'inline-block', 'width': '33%'}
        ),
        html.Div(
            dcc.Slider(
                id='minimum_games_played_slider',
                min=0,
                max=np.max(total_df_with_salaries['games_played']), #change this later
                step=1,
                value=0
                #marks={i: str(i) for i in range(np.max(total_df_with_salaries['games_played'])+1)}
            ),
            style={'display': 'inline-block', 'width': '33%'}
        ),
        html.Div(
            dcc.RangeSlider(
                id='salary_percentile_slider',
                min=0,
                max=41000000,
                step=1000000,
                value=[0, 41000000]
            ),
            style={'display': 'inline-block', 'width': '33%'}
        )
    ]),
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
    # dash_table.DataTable(
    #     id='table-filtering-be',
    #     columns=[{'name': i, "id": i} for i in total_df_with_salaries.columns],
    #     data=total_df_with_salaries.to_dict('records'),
    #     sort_action="native"
    # ),
    html.Div(
        id='table-filtering-be',
        className='tableDiv'
    )
])

@app.callback(
    Output('table-filtering-be', 'children'),
    [Input('fg-weighting', 'value'),
     Input('ft-weighting', 'value'),
     Input('3p-weighting', 'value'),
     Input('reb-weighting', 'value'),
     Input('ast-weighting', 'value'),
     Input('stl-weighting', 'value'),
     Input('blk-weighting', 'value'),
     Input('to-weighting', 'value'),
     Input('ppg-weighting', 'value'),
     Input('checklist-options', 'value')])
def update_table(fg_value, ft_value, three_point_value, rebs, asts, stls, blks,
    tos, ppg, checklist_options):
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
    temp_table = total_df_with_salaries
    temp_table['ppg'] = temp_table.ppg.round(1)
    temp_table['raw_score'] = 0
    for option in checklist_options:
        if option == 'turnovers':
            temp_table['raw_score'] -= normalize(temp_table[option])*weight_dict[option]
        else:
            temp_table['raw_score'] += normalize(temp_table[option])*weight_dict[option]
    temp_table['raw_score'] = (normalize(temp_table['raw_score'])*100).round(2)
    temp_table = temp_table.drop('no_accents', 1)
    temp_table_cols = [{'name': i, 'id': i} for i in temp_table.columns]
    return html.Div([
        dash_table.DataTable(
            id='main-table',
            columns=temp_table_cols,
            data=temp_table.to_dict('rows'),
            sort_action="native",
            fixed_columns={ 'headers': True, 'data': 1 },
            style_cell={
                'minWidth': '100px', 'width': '200px', 'maxWidth': '300px'
            },
            style_table={
                'maxHeight': '800px',
                'maxWidth': '2000px',
                'overflowY': 'scroll'
            }
        )
    ])
