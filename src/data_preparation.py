import pandas as pd
import os.path
import os
from collections import defaultdict
import streamlit as st
from mplsoccer import Sbopen


def get_team_matches(parser, competition_id, season_id, team_name):
    # Get all the matches
    df_season = parser.match(competition_id=competition_id, season_id=season_id)
    df_team = df_season[(df_season['home_team_name'] == team_name) | (df_season['away_team_name'] == team_name)]
    return df_team


def get_events_data(parser, match_files):
    # Get the events data based on the match ids
    df_match_files = pd.concat([parser.event(file)[0] for file in match_files])
    return df_match_files


def add_match_date(df_events, df_season):
    # Add match data to the events
    df = df_events.merge(df_season[['match_id', 'match_week', 'match_date']], on='match_id')
    return df


####################################################################################
# LOAD EVENTS DATA
####################################################################################

folder_name = "data"

# Create the folder "data" if not exists
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
else:
    print(f"Folder '{folder_name}' already exists.")

# Instantiate a parser object
parser = Sbopen()

cfc_files_lst = ['./data/events_18_19_cfc.csv']
afc_files_lst = ['./data/events_18_19_afc.csv']
season_id_lst = [4]


@st.cache_data
def load_data(file, season_id, team_name, df_name_prefix, df_events_prefix, extension=".csv"):
    if not os.path.isfile(file):
        print(f"{file} does not exist in directory.. start loading the data from Statsbomb")
        parser = Sbopen()
        folder, file_name = os.path.split(file)
        file_name_without_extension, _ = os.path.splitext(file_name)
        result = file_name_without_extension.split("_")[-3:]
        season_team = "_".join(result)
        df = get_team_matches(parser, competition_id=37, season_id=season_id, team_name=team_name)
        df_name = df_events_prefix + season_team
        df_events = get_events_data(parser, match_files=df['match_id'].to_list())
        df_events = add_match_date(df_events, df)
        csv_name = df_name[len(df_events_prefix):]
        df_events.to_csv("./data/events_" + csv_name + extension, index=False)
        df_name = df_name_prefix + file.split('/')[-1].split('.')[0]
        globals()[df_name] = df_events


# Load Chelsea FCW events data
for file, season_id in zip(cfc_files_lst, season_id_lst):
    load_data(file, season_id, 'Chelsea FCW', "df_", "df_events_")

# Load Arsenal WFC events data
for file, season_id in zip(afc_files_lst, season_id_lst):
    load_data(file, season_id, 'Arsenal WFC', "df_", "df_events_")


####################################################################################
# CREATE DATAFRAME WITH DATA GROUPED BY MATCH WEEK
####################################################################################


def get_match_week_stat(df, team_name, variable):
    ''' Returns a list with the specified outcome count for each match week.
        If the outcome_name does not occur, the value 0 is added as value to the match_week. '''
    match_weeks = range(1, df["date_number"].max() + 1)
    dct = defaultdict(int)
    for match_week in match_weeks:
        dct[match_week-1] = df[(df["date_number"] == match_week) &
                             (df["team_name"] == team_name) &
                             ((df["outcome_name"] == variable) | (df["type_name"] == variable))].shape[0]
    df = pd.DataFrame.from_dict(dict(dct), orient='index', columns=[variable])
    return df[variable].tolist()


def get_match_week_stat_op(df, team_name, variable):
    ''' Returns a list with the specified outcome count for each match week for the opposing team.
        If the outcome_name does not occur, the value 0 is added as value to the match_week. '''
    match_weeks = range(df["date_number"].min(), df["date_number"].max() + 1)
    dct = defaultdict(int)
    for match_week in match_weeks:
        dct[match_week-1] = df[(df["date_number"] == match_week) &
                             (df["team_name"] != team_name) & ((df["outcome_name"] == variable) | (df["type_name"] == variable))].shape[0]
    df = pd.DataFrame.from_dict(dict(dct), orient='index', columns=[variable])
    return df[variable].tolist()


def get_match_week_stat_nested_calc(df, team_name, event_type, var_type, calc):
    if calc == 'count':
        return df[(df['type_name'] == event_type) &
                  (df['team_name'] == team_name)].groupby('date_number').count()[var_type].tolist()
    elif calc == 'sum':
        return df[(df['type_name'] == event_type) &
                  (df['team_name'] == team_name)].groupby('date_number').sum()[var_type].tolist()
    elif calc == 'mean':
        return df[(df['type_name'] == event_type) &
                  (df['team_name'] == team_name)].groupby('date_number').mean()[var_type].tolist()


@st.cache_data
def generate_match_week_df(df, team_name):
    goals_lst = get_match_week_stat(df, team_name, 'Goal')
    goals_conceded_lst = get_match_week_stat_op(df, team_name, 'Goal')
    shots_lst = get_match_week_stat(df, team_name, 'Shot')
    off_target_lst = get_match_week_stat(df, team_name, 'Off T')
    shot_blocked_lst = get_match_week_stat(df, team_name, 'Blocked')
    shots_saved_lst = get_match_week_stat(df, team_name, 'Saved')
    xg_lst = df.groupby('date_number').sum()['shot_statsbomb_xg'].to_list()
    subs_lst = get_match_week_stat(df, team_name, 'Substitution')
    offs_lst = get_match_week_stat(df, team_name, 'Offside')
    clear_lst = get_match_week_stat(df, team_name, 'Clearance')
    pass_length_lst = get_match_week_stat_nested_calc(df, team_name, 'Pass', 'pass_length', 'sum')
    pass_length_avg_lst = get_match_week_stat_nested_calc(df, team_name, 'Pass', 'pass_length', 'mean')
    pass_cnt_lst = get_match_week_stat_nested_calc(df, team_name, 'Pass', 'pass_length', 'count')
    matches_numbered = df['date_number'].to_list()

    df = pd.DataFrame(list(zip(goals_lst, goals_conceded_lst, shots_lst, off_target_lst, shot_blocked_lst,
                               shots_saved_lst, xg_lst, subs_lst, offs_lst, clear_lst, pass_length_lst,
                               pass_length_avg_lst, pass_cnt_lst)),
                      columns=['GoalsScored', 'GoalsConceded', 'Shots', 'ShotOffT', 'ShotsBlocked', 'ShotsSaved',
                               'ShotXG', 'Substitutions', 'Offsides', 'Clearances', 'PassLengthSum', 'PassLengthAvg',
                               'PassCnt'])

    df = df.reset_index()
    df.rename(columns={'index': 'MatchWeek'}, inplace=True)
    df = df.set_index('MatchWeek')
    df.index = df.index + 1
    return df


####################################################################################
# VARIABLE DESCRIPTIONS
####################################################################################


@st.cache_data
def get_variable_descriptions():
    var_list = [
        ('GoalsScored', 'Number of goals scored'),
        ('GoalsConceded', 'Number of goals conceded'),
        ('Shots', 'Number of shots in the match week'),
        ('ShotOffT', 'Number of shots off target'),
        ('ShotsBlocked', 'Number of shots blocked'),
        ('ShotsSaved', 'Number of shots saved'),
        ('ShotXG', 'Expected goals for shots'),
        ('Clearances', 'Number of clearances'),
        ('PassLengthSum', 'Sum of pass lengths'),
        ('PassLengthAvg', 'Average pass length'),
        ('PassCnt', 'Number of passes')
    ]
    df = pd.DataFrame(var_list, columns=['Variable', 'Description'])
    return df
