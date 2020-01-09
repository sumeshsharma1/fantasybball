def league_analysis(year, leagueid, last_n_days=None):
    from scripts.baseDataCreation import create_base_df, create_daily_df
    from scripts.espnQuery import espn_team_pull
    import pandas as pd
    # Pull team info
    team_dict = espn_team_pull(year=year, leagueid=leagueid)

    # Pull season info
    if last_n_days is None:
        season_df = create_base_df(season_year=2020)
    else:
        season_df = create_daily_df(last_days=last_n_days)
    season_df = season_df[['name', 'field_goal_percentage', 'free_throw_percentage', 'made_three_point_field_goals',
                          'rebounds', 'assists', 'blocks', 'steals', 'turnovers', 'ppg']]
    season_df['ppg'] = round(season_df['ppg'], 1)

    # Convert team info to dataframe
    wide_df = pd.DataFrame.from_dict(team_dict, orient='index')
    wide_df.index.name = 'team_name'
    wide_df.reset_index(inplace = True)

    # Convert team info dataframe from wide to long
    long_df = pd.melt(wide_df, id_vars=['team_name']).drop(columns=['variable']).rename(columns={"value": "player"}).dropna()

    # Merge only players on teams with season df to get their stats, aggregate stats
    merged_df = pd.merge(long_df, season_df, left_on='player', right_on='name')
    agg_df = merged_df.groupby(['team_name'], as_index=False).agg({'field_goal_percentage':'mean',
                                                                'free_throw_percentage':'mean',
                                                                'made_three_point_field_goals':'sum',
                                                                'rebounds':'sum',
                                                                'assists':'sum',
                                                                'blocks':'sum',
                                                                'steals':'sum',
                                                                'turnovers':'sum',
                                                                'ppg': 'mean'}).round(1)

    # Normalize data across league
    normalized_df = agg_df.apply(lambda x: (x - min(x))/(max(x) - min(x)) if (x.name != 'team_name' and x.name != 'turnovers')
                                  else (1 - (x - min(x))/(max(x) - min(x)) if (x.name == 'turnovers') else x))

    # Melt data
    melted_df = pd.melt(normalized_df, id_vars=['team_name'])

    return melted_df
