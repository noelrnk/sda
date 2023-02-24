import cmasher as cmr
import data_preparation as dp
from highlight_text import ax_text
import matplotlib.patheffects as path_effects
from mplsoccer import Pitch, Sbopen, VerticalPitch, FontManager
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.graph_objects as go
import plotly.express as px
import warnings

df_events_18_19_cfc = pd.read_csv('data/events_18_19_cfc.csv')
df_events_18_19_afc = pd.read_csv('data/events_18_19_afc.csv')

df_match_week_cfc_18_19 = dp.generate_match_week_df(df_events_18_19_cfc, 'Chelsea FCW')
df_match_week_afc_18_19 = dp.generate_match_week_df(df_events_18_19_afc, 'Arsenal WFC')


def plot_ind_match_week(df, variables_lst):
    # Create a line plot for each variable in the list
    fig = px.line(df, x='MatchWeek', y=variables_lst, labels={'variable': 'Statistic'},
                  color_discrete_sequence=px.colors.qualitative.Dark24)

    fig.update_layout(width=1200)

    # Add scatter plots for each variable in the list
    for var in variables_lst:
        fig.add_trace(go.Scatter(x=df['MatchWeek'], y=df[var], mode='markers', showlegend=False,
                                 marker_color=fig.data[variables_lst.index(var)].line.color))

    # Set the layout of the plot
    fig.update_layout(title='Match week statistics', xaxis_title='Match Week')
    fig.update_xaxes(tickmode='linear')

    return fig


def plot_match_week_team_comp(df1, df2, variable):
    # Add a team_name column to each DataFrame
    df1['team_name'] = 'Chelsea FCW'
    df2['team_name'] = 'Arsenal WFC'

    # Combine the DataFrames
    df = pd.concat([df1, df2], ignore_index=True)

    # Create a line plot for the variable
    fig = px.line(df, x='MatchWeek', y=variable, labels={'variable': 'Statistic'},
                  color='team_name', color_discrete_sequence=px.colors.qualitative.Dark24)

    # Add scatter plots for the variable
    for i, sub_df in enumerate([df1, df2]):
        fig.add_trace(go.Scatter(x=sub_df['MatchWeek'], y=sub_df[variable], mode='markers',
                                 name=sub_df['team_name'].iloc[0], marker_color=fig.data[i].line.color,
                                 showlegend=False))

    # Set the layout of the plot
    fig.update_layout(title='Match week statistics', xaxis_title='Match Week', width=1200)
    fig.update_xaxes(tickmode='linear')

    return fig


def create_pressure_maps(df, team_name):
    # filter chelsea pressure events
    mask_chelsea_pressure = (df.team_name == team_name) & (df.type_name == 'Pressure')
    df = df.loc[mask_chelsea_pressure, ['x', 'y']]

    path_eff = [path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()]

    # setup pitch
    pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='white')
    fig, axs = pitch.grid(endnote_height=0.03, endnote_space=0, title_height=0.08, title_space=0, axis=False,
                          grid_height=0.84)
    fig.set_facecolor('#f7faf9')

    # heatmap and labels
    bin_statistic = pitch.bin_statistic_positional(df.x, df.y, statistic='count', positional='full', normalize=True)
    pitch.heatmap_positional(bin_statistic, ax=axs['pitch'], cmap='coolwarm', edgecolors='#f7faf9')
    pitch.scatter(df.x, df.y, c='white', s=2, ax=axs['pitch'])
    labels = pitch.label_heatmap(bin_statistic, color='#f4edf0', fontsize=18,
                                 ax=axs['pitch'], ha='center', va='center',
                                 str_format='{:.0%}', path_effects=path_eff)

    if team_name == 'Chelsea FCW':
        axs['title'].text(0.5, 0.5, "Pressure applied by Chelsea", color='#070807',
                          va='center', ha='center', fontsize=20)
    if team_name == 'Arsenal WFC':
        axs['title'].text(0.5, 0.5, "Pressure applied by Arsenal", color='#070807',
                          va='center', ha='center', fontsize=20)
    return fig


def create_shot_map(df, team_name):
    if team_name == 'Chelsea FCW':
        df_shots = df[(df.type_name == 'Shot') & (df.team_name == 'Chelsea FCW')].copy()
        # subset the barca open play passes
        df_pass = df[(df.type_name == 'Pass') &
                     (df.team_name == 'Chelsea FCW') &
                     (~df.sub_type_name.isin(['Throw-in', 'Corner', 'Free Kick', 'Kick Off']))].copy()

    if team_name == 'Arsenal WFC':
        df_shots = df[(df.type_name == 'Shot') & (df.team_name == 'Arsenal WFC')].copy()
        # subset the barca open play passes
        df_pass = df[(df.type_name == 'Pass') &
                     (df.team_name == 'Arsenal WFC') &
                     (~df.sub_type_name.isin(['Throw-in', 'Corner', 'Free Kick', 'Kick Off']))].copy()

    # setup a mplsoccer FontManager to download google fonts (SigmarOne-Regular)
    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/rubikmonoone/'
                           'RubikMonoOne-Regular.ttf')

    pitch = VerticalPitch(pad_top=0.5,  # only a small amount of space at the top of the pitch
                          pad_bottom=-20,  # reduce the area displayed at the bottom of the pitch
                          pad_left=-15,  # reduce the area displayed on the left of the pitch
                          pad_right=-15,  # reduce the area displayed on the right of the pitch
                          half=True,  # half of a pitch
                          goal_type='line')

    # filter goals / non-shot goals
    df_goals = df_shots[df_shots.outcome_name == 'Goal'].copy()
    df_non_goal_shots = df_shots[df_shots.outcome_name != 'Goal'].copy()

    fig, ax = pitch.draw(figsize=(12, 10))

    # plot non-goal shots with hatch
    sc1 = pitch.scatter(df_non_goal_shots.x, df_non_goal_shots.y,
                        # size varies between 100 and 1900 (points squared)
                        s=(df_non_goal_shots.shot_statsbomb_xg * 1900) + 100,
                        edgecolors='#606060',  # give the markers a charcoal border
                        c='None',  # no facecolor for the markers
                        hatch='///',  # the all important hatch (triple diagonal lines)
                        # for other markers types see: https://matplotlib.org/api/markers_api.html
                        marker='o',
                        ax=ax)

    # plot goal shots with a color
    sc2 = pitch.scatter(df_goals.x, df_goals.y,
                        # size varies between 100 and 1900 (points squared)
                        s=(df_goals.shot_statsbomb_xg * 1900) + 100,
                        edgecolors='#606060',  # give the markers a charcoal border
                        c='#b94b75',  # color for scatter in hex format
                        # for other markers types see: https://matplotlib.org/api/markers_api.html
                        marker='o',
                        ax=ax)
    if team_name == 'Chelsea FCW':
        txt = ax.text(x=40, y=85, s='Chelsea shots all season',
                      size=30,
                      fontproperties=fm_rubik.prop, color=pitch.line_color,
                      va='center', ha='center')
    if team_name == 'Arsenal WFC':
        txt = ax.text(x=40, y=85, s='Arsenal shots all season',
                      size=30,
                      fontproperties=fm_rubik.prop, color=pitch.line_color,
                      va='center', ha='center')

    return fig


def create_pass_map(team_name):
    if team_name == 'Chelsea FCW':
        number = 19785
    elif team_name == 'Arsenal WFC':
        number = 19736
    parser = Sbopen()
    events, related, freeze, tactics = parser.event(number)
    lineup = parser.lineup(number)

    # dataframe with player_id and when they were subbed off
    time_off = events.loc[(events.type_name == 'Substitution'),
                          ['player_id', 'minute']]
    time_off.rename({'minute': 'off'}, axis='columns', inplace=True)
    # dataframe with player_id and when they were subbed on
    time_on = events.loc[(events.type_name == 'Substitution'),
                         ['substitution_replacement_id', 'minute']]
    time_on.rename({'substitution_replacement_id': 'player_id',
                    'minute': 'on'}, axis='columns', inplace=True)
    players_on = time_on.player_id
    # merge on times subbed on/off
    lineup = lineup.merge(time_on, on='player_id', how='left')
    lineup = lineup.merge(time_off, on='player_id', how='left')
    # filter the tactics lineup for the starting xi
    starting_ids = events[events.type_name == 'Starting XI'].id
    starting_xi = tactics[tactics.id.isin(starting_ids)]
    starting_players = starting_xi.player_id

    # filter the lineup for players that actually played
    mask_played = ((lineup.on.notnull()) | (lineup.off.notnull()) | (lineup.player_id.isin(starting_players)))
    lineup = lineup[mask_played].copy()

    # get the first position for each player and add this to the lineup dataframe
    player_positions = (events[['player_id', 'position_id']]
                        .dropna(how='any', axis='rows')
                        .drop_duplicates('player_id', keep='first'))
    lineup = lineup.merge(player_positions, how='left', on='player_id')

    # add on the position abbreviation
    formation_dict = {1: 'GK', 2: 'RB', 3: 'RCB', 4: 'CB', 5: 'LCB', 6: 'LB', 7: 'RWB',
                      8: 'LWB', 9: 'RDM', 10: 'CDM', 11: 'LDM', 12: 'RM', 13: 'RCM',
                      14: 'CM', 15: 'LCM', 16: 'LM', 17: 'RW', 18: 'RAM', 19: 'CAM',
                      20: 'LAM', 21: 'LW', 22: 'RCF', 23: 'ST', 24: 'LCF', 25: 'SS'}
    lineup['position_abbreviation'] = lineup.position_id.map(formation_dict)

    # sort the dataframe so the players are
    # in the order of their position (if started), otherwise in the order they came on
    lineup['start'] = lineup.player_id.isin(starting_players)
    lineup.sort_values(['team_name', 'start', 'on', 'position_id'],
                       ascending=[True, False, True, True], inplace=True)
    # if you want the other team set team = team2
    team1, team2 = lineup.team_name.unique()
    team = team1
    lineup_team = lineup[lineup.team_name == team].copy()

    # filter the events to exclude some set pieces
    set_pieces = ['Throw-in', 'Free Kick', 'Corner', 'Kick Off', 'Goal Kick']
    # for the team pass map
    pass_receipts = events[(events.team_name == team) & (events.type_name == 'Ball Receipt')].copy()
    # for the player pass maps
    passes_excl_throw = events[(events.team_name == team) & (events.type_name == 'Pass') &
                               (events.sub_type_name != 'Throw-in')].copy()

    # identify how many players played and how many subs were used
    # we will use this in the loop for only plotting pass maps for as
    # many players who played
    num_players = len(lineup_team)
    num_sub = num_players - 11

    # add padding to the top so we can plot the titles, and raise the pitch lines
    pitch = Pitch(pad_top=10, line_zorder=2)

    # arrow properties for the sub on/off
    green_arrow = dict(arrowstyle='simple, head_width=0.7',
                       connectionstyle="arc3,rad=-0.8", fc="green", ec="green")
    red_arrow = dict(arrowstyle='simple, head_width=0.7',
                     connectionstyle="arc3,rad=-0.8", fc="red", ec="red")

    # a fontmanager object for using a google font
    fm_scada = FontManager('https://raw.githubusercontent.com/googlefonts/scada/main/fonts/ttf/'
                           'Scada-Regular.ttf')


    # filtering out some highlight_text warnings - the warnings aren't correct as the
    # text fits inside the axes.
    warnings.simplefilter("ignore", UserWarning)

    # plot the 5 * 3 grid
    fig, axs = pitch.grid(nrows=5, ncols=3, figheight=30,
                          endnote_height=0.03, endnote_space=0,
                          # Turn off the endnote/title axis. I usually do this after
                          # I am happy with the chart layout and text placement
                          axis=False,
                          title_height=0.08, grid_height=0.84)
    # cycle through the grid axes and plot the player pass maps
    for idx, ax in enumerate(axs['pitch'].flat):
        # only plot the pass maps up to the total number of players
        if idx < num_players:
            # filter the complete/incomplete passes for each player (excudes throw-ins)
            lineup_player = lineup_team.iloc[idx]
            player_id = lineup_player.player_id
            player_pass = passes_excl_throw[passes_excl_throw.player_id == player_id]
            complete_pass = player_pass[player_pass.outcome_name.isnull()]
            incomplete_pass = player_pass[player_pass.outcome_name.notnull()]

            # plot the arrows
            pitch.arrows(complete_pass.x, complete_pass.y,
                         complete_pass.end_x, complete_pass.end_y,
                         color='#56ae6c', width=2, headwidth=4, headlength=6, ax=ax)
            pitch.arrows(incomplete_pass.x, incomplete_pass.y,
                         incomplete_pass.end_x, incomplete_pass.end_y,
                         color='#7065bb', width=2, headwidth=4, headlength=6, ax=ax)

            # plot the title for each player axis
            # here we use f-strings to combine the variables from the dataframe and text
            # we plot the title at x=0, y=-5
            # this is the left hand-side of the pitch (x=0) and between
            # top of the y-axis (y=0) and the top of the padding (y=-10, remember pad_top = 10)
            # note that the StatsBomb y-axis is inverted, so you may need
            # to change this if you use another pitch_type (e.g. 'uefa').
            # We also use the highlight-text package to highlight complete_pass green
            # so put <> around the number of completed passes.
            total_pass = len(complete_pass) + len(incomplete_pass)
            annotation_string = (f'{lineup_player.position_abbreviation} | '
                                 f'{lineup_player.player_name} | '
                                 f'<{len(complete_pass)}>/{total_pass} | '
                                 f'{round(100 * len(complete_pass) / total_pass, 1)}%')
            ax_text(0, -5, annotation_string, ha='left', va='center', fontsize=13,
                    fontproperties=fm_scada.prop,  # using the fontmanager for the google font
                    highlight_textprops=[{"color": '#56ae6c'}], ax=ax)

            # add information for subsitutions on/off and arrows
            if not np.isnan(lineup_team.iloc[idx].off):
                ax.text(116, -10, str(lineup_team.iloc[idx].off.astype(int)), fontsize=20,
                        fontproperties=fm_scada.prop,
                        ha='center', va='center')
                ax.annotate('', (120, -2), (112, -2), arrowprops=red_arrow)
            if not np.isnan(lineup_team.iloc[idx].on):
                ax.text(104, -10, str(lineup_team.iloc[idx].on.astype(int)), fontsize=20,
                        fontproperties=fm_scada.prop,
                        ha='center', va='center')
                ax.annotate('', (108, -2), (100, -2), arrowprops=green_arrow)

    # plot on the last Pass Map
    # (note ax=ax as we have cycled through to the last axes in the loop)
    pitch.kdeplot(x=pass_receipts.x, y=pass_receipts.y, ax=ax,
                  cmap=cmr.lavender,
                  levels=100,
                  thresh=0, fill=True)
    ax.text(0, -5, f'{team}: Pass Receipt Heatmap', ha='left', va='center',
            fontsize=20, fontproperties=fm_scada.prop)

    # remove unused axes (if any)
    for ax in axs['pitch'].flat[11 + num_sub:-1]:
        ax.remove()

    # title text
    axs['title'].text(0.5, 0.65, f'{team1} Pass Maps vs {team2}', fontsize=40,
                      fontproperties=fm_scada.prop, va='center', ha='center')
    SUB_TEXT = ('Player Pass Maps: exclude throw-ins only\n'
                'Team heatmap: includes all attempted pass receipts')
    axs['title'].text(0.5, 0.35, SUB_TEXT, fontsize=20,
                      fontproperties=fm_scada.prop, va='center', ha='center')

    return fig
