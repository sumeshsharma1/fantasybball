def create_base_df(season_year):
    from basketball_reference_web_scraper import client
    import pandas as pd
    import unicodedata

    season_stats = client.players_season_totals(season_end_year=season_year)
    total_df = pd.DataFrame(season_stats)

    total_df['positions'], total_df['team'] = total_df['positions'].astype(str), total_df['team'].astype(str)

    positions = {"[<Position.CENTER: 'CENTER'>]": "C",
                 "[<Position.SHOOTING_GUARD: 'SHOOTING GUARD'>]": "SG",
                 "[<Position.POWER_FORWARD: 'POWER FORWARD'>]": "PF",
                 "[<Position.SMALL_FORWARD: 'SMALL FORWARD'>]": "SF",
                 "[<Position.POINT_GUARD: 'POINT GUARD'>]": "PG",
                 "[<Position.GUARD: 'GUARD'>]": "SG"}
    team_sub = {"Team.": "",
                "_": ' '}

    total_df = total_df.replace(positions).replace(team_sub, regex=True)
    total_df['no_accents'] = total_df['name'].apply(
        lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode('UTF-8').replace(".", ""))

    total_df = total_df.groupby(['slug', 'name', 'no_accents'], as_index=False).agg({'made_three_point_field_goals':'sum',
                                                                                   'attempted_three_point_field_goals': 'sum',
                                                                                   'made_field_goals': 'sum',
                                                                                   'made_free_throws': 'sum',
                                                                                   'games_played': 'sum',
                                                                                   'attempted_field_goals':'sum',
                                                                                   'attempted_free_throws':'sum',
                                                                                   'offensive_rebounds':'sum',
                                                                                   'defensive_rebounds': 'sum',
                                                                                   'assists':'sum',
                                                                                   'blocks':'sum',
                                                                                   'steals':'sum',
                                                                                   'turnovers':'sum',
                                                                                   'team': 'last',
                                                                                   'positions': 'last',
                                                                                   'games_played': 'sum'}).drop_duplicates()

    total_df = total_df.assign(
        field_goal_percentage=(total_df['made_field_goals'] * 100 / total_df['attempted_field_goals']).round(1),
        three_point_field_goal_percentage=(total_df['made_three_point_field_goals'] * 100 / total_df[
            'attempted_three_point_field_goals']).round(1),
        free_throw_percentage=(total_df['made_free_throws'] * 100 / total_df['attempted_free_throws']).round(1),
        rebounds=total_df['offensive_rebounds'] + total_df['defensive_rebounds']).fillna(0)


    salaries = pd.read_csv("nba_beta_salary.csv", sep=",", engine='python')

    total_df_with_salaries = total_df.join(salaries[['slug', '2024-25']].set_index('slug'), on='slug').dropna()

    total_df_with_salaries = total_df_with_salaries.drop('slug', axis=1)

    total_df_with_salaries['points'] = (2 * (
            total_df_with_salaries['made_field_goals'] - total_df_with_salaries['made_three_point_field_goals']) + \
                                 3 * (total_df_with_salaries['made_three_point_field_goals']) +
                                 total_df_with_salaries['made_free_throws'])

    total_df_with_salaries['ppg'] = (2 * (
                total_df_with_salaries['made_field_goals'] - total_df_with_salaries['made_three_point_field_goals']) + \
                                     3 * (total_df_with_salaries['made_three_point_field_goals']) +
                                     total_df_with_salaries['made_free_throws']) / \
                                    total_df_with_salaries['games_played']

    total_df_with_salaries = total_df_with_salaries.drop_duplicates()
    total_df_with_salaries['avg_fantasy_pts'] = (2*total_df_with_salaries['made_field_goals'] - total_df_with_salaries['attempted_field_goals'] + \
        total_df_with_salaries['made_free_throws'] - total_df_with_salaries['attempted_free_throws'] + total_df_with_salaries['made_three_point_field_goals'] + \
        total_df_with_salaries['rebounds'] + 2*total_df_with_salaries['assists'] + 4*total_df_with_salaries['steals'] + \
        4*total_df_with_salaries['blocks'] - 2*total_df_with_salaries['turnovers'] + total_df_with_salaries['points'])/total_df_with_salaries['games_played']

    return total_df_with_salaries

def create_daily_df(last_days):
    from basketball_reference_web_scraper import client
    import pandas as pd
    from datetime import date, timedelta
    import unicodedata

    curr_date = date.today()
    df = pd.DataFrame(client.player_box_scores(day=curr_date.day, month=curr_date.month, year=curr_date.year))

    for i in range(1,last_days+1):
        temp_date = date.today() - timedelta(days = i)
        temp_df = pd.DataFrame(client.player_box_scores(day=temp_date.day, month=temp_date.month, year=temp_date.year))
        df = pd.concat([df, temp_df])

    df = df.assign(
        points=2*(df['made_field_goals'] - df['made_three_point_field_goals']) + 3*df['made_three_point_field_goals'] + df['made_free_throws'],
        rebounds=df['defensive_rebounds'] + df['offensive_rebounds'],
        field_goal_percentage=(df['made_field_goals'] * 100 /df['attempted_field_goals']).fillna(0).round(2),
        free_throw_percentage=(df['made_free_throws'] * 100 /df['attempted_free_throws']).fillna(0).round(2)
    )

    df = df[['name', 'field_goal_percentage', 'free_throw_percentage', 'made_three_point_field_goals',
            'rebounds','assists', 'blocks', 'steals','turnovers', 'points', 'attempted_field_goals',
            'attempted_free_throws', 'slug']]

    df = df.groupby(['name', 'slug'], as_index=False).agg({'field_goal_percentage':'mean',
                                                       'free_throw_percentage':'mean',
                                                       'made_three_point_field_goals':'sum',
                                                       'attempted_field_goals':'sum',
                                                       'attempted_free_throws':'sum',
                                                       'rebounds':'sum',
                                                       'assists':'sum',
                                                       'blocks':'sum',
                                                       'steals':'sum',
                                                       'turnovers':'sum',
                                                       'points':'mean'}).rename(columns={'points':'ppg'})

    df['field_goal_percentage'] = df['field_goal_percentage'].round(1)
    df['free_throw_percentage'] = df['free_throw_percentage'].round(1)
    df['ppg'] = df['ppg'].round(1)

    df['no_accents'] = df['name'].apply(
        lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode('UTF-8').replace(".", ""))
    # df.no_accents[df.no_accents == 'Taurean Waller-Prince'] = 'Taurean Prince'

    salaries = pd.read_csv("nba_beta_salary.csv", sep=",", engine='python')
    total_df_with_salaries = df.join(salaries[['slug', '2024-25']].set_index('slug'), on='slug').dropna()
    total_df_with_salaries = total_df_with_salaries.drop('slug', axis=1)

    total_df_with_salaries['points'] = (2 * (
            total_df_with_salaries['made_field_goals'] - total_df_with_salaries['made_three_point_field_goals']) + \
                                 3 * (total_df_with_salaries['made_three_point_field_goals']) +
                                 total_df_with_salaries['made_free_throws'])

    total_df_with_salaries['ppg'] = (2 * (
                total_df_with_salaries['made_field_goals'] - total_df_with_salaries['made_three_point_field_goals']) + \
                                     3 * (total_df_with_salaries['made_three_point_field_goals']) +
                                     total_df_with_salaries['made_free_throws']) / \
                                    total_df_with_salaries['games_played']

    total_df_with_salaries = total_df_with_salaries.drop_duplicates()
    total_df_with_salaries['avg_fantasy_pts'] = (2*total_df_with_salaries['made_field_goals'] - total_df_with_salaries['attempted_field_goals'] + \
        total_df_with_salaries['made_free_throws'] - total_df_with_salaries['attempted_free_throws'] + total_df_with_salaries['made_three_point_field_goals'] + \
        total_df_with_salaries['rebounds'] + 2*total_df_with_salaries['assists'] + 4*total_df_with_salaries['steals'] + \
        4*total_df_with_salaries['blocks'] - 2*total_df_with_salaries['turnovers'] + total_df_with_salaries['points'])/total_df_with_salaries['games_played']

    return total_df_with_salaries
