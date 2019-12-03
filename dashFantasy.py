def create_base_df(season_year):
    from basketball_reference_web_scraper import client
    import pandas as pd
    import unicodedata

    advanced_stats = client.players_advanced_season_totals(season_end_year=season_year)
    season_stats = client.players_season_totals(season_end_year=season_year)
    advanced_stats_df = pd.DataFrame(advanced_stats)[['age', 'box_plus_minus', 'true_shooting_percentage',
                                                      'value_over_replacement_player', 'win_shares',
                                                      'slug']]
    season_stats_df = pd.DataFrame(season_stats)

    total_df = season_stats_df.join(advanced_stats_df.set_index(['slug', 'age']), on=['slug', 'age'])
    total_df['positions'], total_df['team'] = total_df['positions'].astype(str), total_df['team'].astype(str)

    positions = {"[<Position.CENTER: 'CENTER'>]": "C",
                 "[<Position.SHOOTING_GUARD: 'SHOOTING GUARD'>]": "SG",
                 "[<Position.POWER_FORWARD: 'POWER FORWARD'>]": "PF",
                 "[<Position.SMALL_FORWARD: 'SMALL FORWARD'>]": "SF",
                 "[<Position.POINT_GUARD: 'POINT GUARD'>]": "PG"}
    team_sub = {"Team.": "",
                "_": ' '}

    total_df = total_df.replace(positions).replace(team_sub, regex=True)

    total_df = total_df.assign(
        field_goal_percentage=(total_df['made_field_goals'] * 100 / total_df['attempted_field_goals']).round(1),
        three_point_field_goal_percentage=(total_df['made_three_point_field_goals'] * 100 / total_df[
            'attempted_three_point_field_goals']).round(1),
        free_throw_percentage=(total_df['made_free_throws'] * 100 / total_df['attempted_free_throws']).round(1),
        true_shooting_percentage=total_df['true_shooting_percentage'] * 100).fillna(0)

    total_df['no_accents'] = total_df['name'].apply(
        lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode('UTF-8').replace(".", ""))
    total_df.no_accents[total_df.no_accents == 'Taurean Waller-Prince'] = 'Taurean Prince'

    salaries = pd.read_csv("C:/Users/ssharma2/Desktop/nba_beta_salary.csv", sep=",", engine='python')

    total_df_with_salaries = total_df.join(salaries[['slug', '2019-20']].set_index('slug'), on='slug').dropna()

    total_df_with_salaries = total_df_with_salaries.drop('slug', axis=1)

    total_df_with_salaries['rebounds'] = total_df_with_salaries['offensive_rebounds'] + total_df_with_salaries[
        'defensive_rebounds']
    total_df_with_salaries['ppg'] = (2 * (
                total_df_with_salaries['made_field_goals'] - total_df_with_salaries['made_three_point_field_goals']) + \
                                     3 * (total_df_with_salaries['made_three_point_field_goals']) +
                                     total_df_with_salaries['made_free_throws']) / \
                                    total_df_with_salaries['games_played']

    return total_df_with_salaries

total_df_with_salaries = create_base_df(season_year=2020)

def init_js():
    from IPython.core.display import HTML
    % % javascript
    require.config({
        paths: {
            DT: '//cdn.datatables.net/1.10.19/js/jquery.dataTables.min',
        }
    });
    require(["DT"], function(DT)
    {
    $(document).ready(() = > {
    $("#PlayerTable").DataTable();
    })
    });
    $('head').append(
        '<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css">');

def init_datatable_mode():
    """Initialize DataTable mode for pandas DataFrame represenation."""
    import pandas as pd
    from IPython.core.display import display, Javascript

    # configure path to the datatables library using requireJS
    # that way the library will become globally available
    display(Javascript("""
        require.config({
            paths: {
                DT: '//cdn.datatables.net/1.10.19/js/jquery.dataTables.min',
            }
        });
        $('head').append('<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css">');
    """))

    def _repr_datatable_(self):
        """Return DataTable representation of pandas DataFrame."""
        # classes for dataframe table (optional)
        classes = ['table', 'table-striped', 'table-bordered']

        # create table DOM
        script = (
            f'$(element).html(`{self.to_html(index=False, classes=classes)}`);\n'
        )

        # execute jQuery to turn table into DataTable
        script += """
            require(["DT"], function(DT) {
                $(document).ready( () => {
                    // Turn existing table into datatable
                    $(element).find("table.dataframe").DataTable( {
                    scrollY: "300px",
                    scrollX: true,
                    scrollCollapse: true,
                    paging: false,
                    columnDefs: [
                    { targets: [ 0, 3 ], className: 'dt-body-nowrap' }
                    ],
                    autoWidth: true,
                    });
                })
            });
        """

        return script

    pd.DataFrame._repr_javascript_ = _repr_datatable_


pos = ['All'] + sorted(total_df_with_salaries['positions'].unique().tolist())
team = ['All'] + sorted(total_df_with_salaries['team'].unique().tolist())

import ipywidgets as widgets
from IPython.display import display
from IPython.html.widgets import interactive, interact, HBox, Layout, VBox
from IPython.core.display import display, HTML
from re import sub
from decimal import Decimal
import math

pd.options.mode.chained_assignment = None
pd.set_option('display.expand_frame_repr', False)

display(HTML("<style>.container { width:100% !important; }</style>"))

def normalize(array):
    return np.asarray([float(i) / np.max(array) for i in array])


def espn_fantasy_pull(year, leagueid):
    import requests
    import csv
    from datetime import datetime, timedelta
    import locale
    locale.setlocale(locale.LC_ALL, '')
    currentdate = datetime.now()
    futuredate = currentdate + timedelta(days=7)

    url = "https://fantasy.espn.com/apis/v3/games/fba/seasons/" + str(year) + "/segments/0/leagues/" + str(leagueid)

    teamdata = requests.get(url).json()
    matchups = requests.get(url, params={"view": "mMatchup"}).json()

    teamMap = {}

    for team in teamdata['teams']:
        teamMap[team['id']] = team['location'] + " " + team['nickname']

    player_list = []

    for j in range(len(matchups['teams'])):
        for i in range(len(matchups['teams'][j]['roster']['entries'])):
            player = matchups['teams'][j]['roster']['entries'][i]['playerPoolEntry']['player']['fullName']
            if player[-3:] in ['Jr.', 'Sr.', 'III']:
                player = player[:-4]
            elif player[-3:] == " II":
                player = player[:-3]
            else:
                player = player
            player = player.replace(".", "")
            player_list.append(player)
    return player_list


player_list = espn_fantasy_pull(year=2020, leagueid=22328189)


def position_view(Position='', Team='', FG='', Min_Percentile='',
                  FT='', ThreePoint='', Reb='', Ast='', Stl='',
                  Blk='', TO='', PPG='', Min_Games_Played='', FG_Weight='',
                  FT_Weight='', ThreePoint_Weight='', Reb_Weight='', PPG_Weight='',
                  Ast_Weight='', Stl_Weight='', Blk_Weight='', TO_Weight='',
                  Salary='', Fantasy_Filter=''):
    # Filter games first, and then minutes
    left_salary = Decimal(sub(r'[^\d.]', '', Salary[0]))
    right_salary = Decimal(sub(r'[^\d.]', '', Salary[1]))

    total_df_return = total_df_with_salaries[
        (total_df_with_salaries['minutes_played'] / total_df_with_salaries['games_played'] <=
         np.percentile(total_df_with_salaries['minutes_played'] / total_df_with_salaries['games_played'],
                       Min_Percentile[1])) &
        (total_df_with_salaries['minutes_played'] / total_df_with_salaries['games_played'] >=
         np.percentile(total_df_with_salaries['minutes_played'] / total_df_with_salaries['games_played'],
                       Min_Percentile[0])) &
        (total_df_with_salaries['games_played'] >= Min_Games_Played) &
        (total_df_with_salaries['2019-20'].replace('[\$,]', '', regex=True).astype(float) >= left_salary) &
        (total_df_with_salaries['2019-20'].replace('[\$,]', '', regex=True).astype(float) <= right_salary)]
    if Fantasy_Filter:
        available_list = list(set(total_df_return['no_accents']) - set(player_list))
        total_df_return = total_df_return[total_df_return['no_accents'].isin(available_list)]

    checkbox_list = []
    sumesh_score_list = []
    checkbox_choices = ['field_goal_percentage', 'free_throw_percentage', 'made_three_point_field_goals',
                        'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'ppg']
    weight_dict = {'field_goal_percentage': FG_Weight,
                   'free_throw_percentage': FT_Weight,
                   'made_three_point_field_goals': ThreePoint_Weight,
                   'rebounds': Reb_Weight,
                   'assists': Ast_Weight,
                   'steals': Stl_Weight,
                   'blocks': Blk_Weight,
                   'turnovers': TO_Weight,
                   'ppg': PPG_Weight}

    for index, value in enumerate([FG, FT, ThreePoint, Reb, Ast, Stl, Blk, TO, PPG]):
        if value:
            sumesh_score_list.append(checkbox_choices[index])
    print(sumesh_score_list)

    total_df_return['sumesh score'] = 0
    total_df_return['raw score'] = 0
    for stat in sumesh_score_list:
        if stat == 'turnovers':
            total_df_return['sumesh score'] -= normalize(total_df_return[stat]) * float(weight_dict[stat][:-1]) \
                                               / total_df_return['2019-20'].replace('[\$,]', '', regex=True).astype(
                float)
            total_df_return['raw score'] -= normalize(total_df_return[stat]) * float(weight_dict[stat][:-1])
        else:
            total_df_return['sumesh score'] += normalize(total_df_return[stat]) * float(weight_dict[stat][:-1]) \
                                               / total_df_return['2019-20'].replace('[\$,]', '', regex=True).astype(
                float)
            total_df_return['raw score'] += normalize(total_df_return[stat]) * float(weight_dict[stat][:-1])

    total_df_return['sumesh score'] = 100 * (total_df_return['sumesh score'] -
                                             np.min(total_df_return['sumesh score'])) / (
                                                  np.max(total_df_return['sumesh score']) -
                                                  np.min(total_df_return['sumesh score']))
    total_df_return['raw score'] = 100 * (total_df_return['raw score'] -
                                          np.min(total_df_return['raw score'])) / (
                                               np.max(total_df_return['raw score']) -
                                               np.min(total_df_return['raw score']))

    if 'All' in Position:
        Position_2 = sorted(total_df_with_salaries['positions'].unique().tolist())
    else:
        Position_2 = Position

    if Team == 'All':
        Team_2 = sorted(total_df_with_salaries['team'].unique().tolist())
    else:
        Team_2 = [Team]

    total_df_return = total_df_return.drop(['no_accents'], axis=1)

    display(total_df_return[(total_df_return['positions'].isin(Position_2)) &
                            (total_df_return['team'].isin(Team_2))])
    return total_df_return[(total_df_return['positions'].isin(Position_2)) &
                           (total_df_return['team'].isin(Team_2))]


min_salary = (np.min(total_df_with_salaries['2019-20'].replace('[\$,]', '', regex=True).astype(float)))
max_salary = (np.max(total_df_with_salaries['2019-20'].replace('[\$,]', '', regex=True).astype(float)))
salary_values = np.arange(math.floor(min_salary / 1000000) * 1000000, math.ceil(max_salary / 1000000) * 1000000 + 1,
                          1000000).tolist()
salary_options = ['${:,.0f}'.format(salary) for salary in salary_values]

pos_widgets = widgets.SelectMultiple(options=pos)
team_widgets = widgets.Combobox(placeholder='Team',
                                options=team)
fg_widgets = widgets.Checkbox(description='FG%',
                              value=True)
ft_widgets = widgets.Checkbox(description='FT%',
                              value=True)
three_point_widgets = widgets.Checkbox(description='3P%',
                                       value=True)
reb_widgets = widgets.Checkbox(description='Reb',
                               value=True)
ast_widgets = widgets.Checkbox(description="Ast",
                               value=True)
stl_widgets = widgets.Checkbox(description='Stl',
                               value=True)
blk_widgets = widgets.Checkbox(description='Blk',
                               value=True)
to_widgets = widgets.Checkbox(description='TO',
                              value=True)
ppg_widgets = widgets.Checkbox(description='PPG',
                               value=True)
min_percentile_widgets = widgets.IntRangeSlider(value=[0, 100],
                                                min=0,
                                                max=100,
                                                step=1,
                                                description='Minutes Percentile:',
                                                continuous_update=False,
                                                layout=Layout(flex='1 1 auto'))
min_games_played_widgets = widgets.IntSlider(value=np.min(total_df_with_salaries['games_played']),
                                             min=np.min(total_df_with_salaries['games_played']),
                                             max=np.max(total_df_with_salaries['games_played']),
                                             step=1,
                                             description='Minimum Games Played:',
                                             continuous_update=False,
                                             layout=Layout(flex='1 1 auto'))
salary_widgets = widgets.SelectionRangeSlider(options=salary_options,
                                              index=(0, len(salary_values) - 1),
                                              description='Salary Range',
                                              layout=Layout(flex='1 1 auto'))
fg_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                     value='1x',
                                     description='FG Weight')
ft_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                     value='1x',
                                     description='FT Weight')
three_point_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                              value='1x',
                                              description='3P Weight')
reb_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                      value='1x',
                                      description='Reb Weight')
ast_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                      value='1x',
                                      description='Ast Weight')
stl_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                      value='1x',
                                      description='Stl Weight')
blk_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                      value='1x',
                                      description='Blk Weight')
to_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                     value='1x',
                                     description='TO Weight')
ppg_weight_widgets = widgets.Dropdown(options=['0x', '0.5x', '1x', '1.5x', '2x'],
                                      value='1x',
                                      description='PPG Weight')
fantasy_filter_widgets = widgets.Checkbox(value=False,
                                          description='Available in your fantasy league')

w = interactive(position_view,
                Position=pos_widgets,
                Team=team_widgets,
                FG=fg_widgets,
                FT=ft_widgets,
                ThreePoint=three_point_widgets,
                Reb=reb_widgets,
                Ast=ast_widgets,
                Stl=stl_widgets,
                Blk=blk_widgets,
                TO=to_widgets,
                PPG=ppg_widgets,
                Min_Percentile=min_percentile_widgets,
                Min_Games_Played=min_games_played_widgets,
                Salary=salary_widgets,
                FG_Weight=fg_weight_widgets,
                FT_Weight=ft_weight_widgets,
                ThreePoint_Weight=three_point_weight_widgets,
                Reb_Weight=reb_weight_widgets,
                Ast_Weight=ast_weight_widgets,
                Stl_Weight=stl_weight_widgets,
                Blk_Weight=blk_weight_widgets,
                TO_Weight=to_weight_widgets,
                PPG_Weight=ppg_weight_widgets,
                Fantasy_Filter=fantasy_filter_widgets)

slider_box_layout = Layout(display='flex',
                           flex_flow='row',
                           align_items='stretch')
first_line = HBox([pos_widgets, team_widgets, fantasy_filter_widgets])
second_line = HBox([min_percentile_widgets, min_games_played_widgets, salary_widgets], layout=slider_box_layout)
third_line = HBox(
    [fg_widgets, ft_widgets, three_point_widgets, reb_widgets, ast_widgets, stl_widgets, blk_widgets, to_widgets,
     ppg_widgets])
fourth_line = HBox(
    [fg_weight_widgets, ft_weight_widgets, three_point_weight_widgets, reb_weight_widgets, ast_weight_widgets,
     stl_weight_widgets,
     blk_weight_widgets, to_weight_widgets, ppg_weight_widgets])
VBox([first_line, second_line, third_line, fourth_line, w.children[-1]])

