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

    salaries = pd.read_csv("nba_beta_salary.csv", sep=",", engine='python')

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
#
# total_df_with_salaries = create_base_df(season_year=2020)
#
# total_df_with_salaries.to_csv('C:/Users/ssharma2/Desktop/fantasybball/total_df_with_salaries.csv',
#                               index = False)
