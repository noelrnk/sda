import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
import data_preparation as dp
import visualizations as vz


st.image('https://www.coolisache.ch/wp-content/uploads/2023/02/fa_women_super_league.jpg')
st.title("FA Women's Super League Analysis")
st.text('Welcome to this Streamlit app! In this dashboard, the 2018/19 season of the Arsenal WFC and the Chelsea FCW '
        'is analysed.')


df_events_18_19_cfc = pd.read_csv('data/events_18_19_cfc.csv')
df_events_18_19_afc = pd.read_csv('data/events_18_19_afc.csv')

df_match_week_cfc_18_19 = dp.generate_match_week_df(df_events_18_19_cfc, 'Chelsea FCW')
df_match_week_afc_18_19 = dp.generate_match_week_df(df_events_18_19_afc, 'Arsenal WFC')


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Intro", "Match Week Stats (Team individual)",
                                              "Match Week Stats (Team Comparison)", "Season Stats",
                                              "Arsenal vs. Chelsea", "Instructions and Data Sources"])


# TAB 1: INTRO
with tab1:
    st.markdown("On the 31st of July 2022, the England forward Chloe Kelly scored the winning goal in the UEFA Women's "
                "Euro final in front of a sold-out Wembley stadium. The tournament underlined the increasing interest "
                "in women's football. An increasing interest in women's football can also be observed in the FA "
                "Women's Super League where Emma Hayes' Chelsea dominated the league in recent years, having won the "
                "league six times since 2015.")
    st.markdown("The 2018/19 season included eleven teams: Arsenal, Birmingham City, Brighton & Hove Albion, Bristol "
                "City, Chelsea, Everton, Liverpool, Manchester City, Reading, West Ham United and Yeovil Town. The "
                "season started on the 9th September 2018 and ended on the 11th May 2019. The season was won by "
                "Arsenal with 54 points, followed by Manchester City with 47 points and Chelsea with 42 points.")

    st.markdown("In this dashboard, the 2018/19 season of Arsenal and Chelsea are analyzed. The analysis includes "
                "match week statistics, a look into the heatmaps and an analysis of the two matches played against "
                "another.")


# TAB 2: MATCH WEEK STATS (TEAM INDIVIDUAL)
with tab2:
    with st.expander("**Individual Team Analysis**", expanded=True):
        col1, col2 = st.columns([2, 2])
        with col1:
            stats_lst = st.multiselect(label='Select the variables',
                                       options=['GoalsScored', 'GoalsConceded', 'Shots', 'ShotOffT', 'ShotsBlocked',
                                                'ShotsSaved', 'ShotXG', 'Clearances', 'PassLengthSum', 'PassLengthAvg',
                                                'PassCnt'])
        with col2:
            team_selection = st.selectbox(label='Select the team', options=['Arsenal WFC', 'Chelsea FCW'])
        if team_selection == 'Arsenal WFC':
            st.plotly_chart(vz.plot_ind_match_week(df_match_week_afc_18_19, stats_lst), use_container_width=True)
        if team_selection == 'Chelsea FCW':
            st.plotly_chart(vz.plot_ind_match_week(df_match_week_cfc_18_19, stats_lst), use_container_width=True)

    with st.expander("**Variable information**", expanded=False):
        st.markdown("Several variables of each match week were aggregated. The variables are described below:")
        st.table(dp.get_variable_descriptions())


# TAB 3: MATCH WEEK STATS (TEAM COMPARISON)
with tab3:
    with st.expander("**Team Comparison**", expanded=True):
        stat = st.selectbox(label='Select the variable', options=['GoalsScored', 'GoalsConceded', 'Shots',
                                                                  'ShotOffT', 'ShotsBlocked', 'ShotsSaved',
                                                                  'ShotXG', 'Clearances', 'PassLengthSum',
                                                                  'PassLengthAvg', 'PassCnt'])

        st.plotly_chart(vz.plot_match_week_team_comp(df_match_week_cfc_18_19, df_match_week_afc_18_19, stat),
                        use_container_width=True)

    with st.expander("**Variable information**", expanded=False):
        st.markdown("Several variables of each match week were aggregated. The variables are described below:")
        st.table(dp.get_variable_descriptions())


# TAB 4: SEASON STATS
with tab4:
    tab3_input = st.selectbox('Select the graph:', ['Pressure map', 'Shot map'])
    if tab3_input == 'Pressure map':
        st.markdown("The pressure maps show the pressure applied in the different areas of the pitch.")
        col1, col2, col3 = st.columns([2, 0.8, 2])
        with col1:
            fig = vz.create_pressure_maps(df_events_18_19_cfc, 'Chelsea FCW')
            st.pyplot(fig)
        with col2:
            st.markdown("")
        with col3:
            fig = vz.create_pressure_maps(df_events_18_19_afc, 'Arsenal WFC')
            st.pyplot(fig)
    if tab3_input == 'Shot map':
        st.markdown("The plots show the attempted shots over the course of the season, whereas the goals are "
                    "highlighted in red.")
        col1, col2 = st.columns([2, 2])
        with col1:
            st.pyplot(vz.create_shot_map(df_events_18_19_cfc, 'Chelsea FCW'))
        with col2:
            st.pyplot(vz.create_shot_map(df_events_18_19_afc, 'Arsenal WFC'))


# TAB 5: ARSENAL VS CHELSEA
with tab5:
    col1, col2 = st.columns([2, 2])
    with col1:
        selected_match = st.selectbox('Select the match:', ['Chelsea (0) - Arsenal (5): 14.10.2018 15:00',
                                                            'Arsenal (1) - Chelsea (2): 13.01.2019 13:30'])
    with col2:
        selected_team = st.selectbox('Select the team:', ['Chelsea FCW', 'Arsenal WFC'], key='team_selection')

    st.markdown('---')

    if selected_match == 'Chelsea (0) - Arsenal (5): 14.10.2018 15:00':
        st.markdown("The match between Chelsea and Arsenal took place on the 14th of October 2018 at Kingsmeadow "
                    "Stadium. The match ended with a 5-0 victory for Arsenal. The following plot shows the passes of "
                    "each player of this match.")
        if selected_team == 'Chelsea FCW':
            st.pyplot(vz.create_pass_map('first', 'home'))
        if selected_team == 'Arsenal WFC':
            st.pyplot(vz.create_pass_map('first', 'away'))

    if selected_match == 'Arsenal (1) - Chelsea (2): 13.01.2019 13:30':
        st.markdown("The match between Arsenal and Chelsea took place on the 13th of January 2019 at Meadow Park. "
                    "The following plot shows the passes of each player of this match.")
        if selected_team == 'Chelsea FCW':
            st.pyplot(vz.create_pass_map('second', 'away'))
        if selected_team == 'Arsenal WFC':
            st.pyplot(vz.create_pass_map('second', 'home'))


# TAB 6: INSTRUCTIONS AND DATA SOURCES
with tab6:
    st.markdown("The data is sourced from [StatsBomb](https://statsbomb.com/) and accessed using the "
                "StatsBomb API for which a function is implemented in the "
                "[mplsoccer](https://mplsoccer.readthedocs.io/en/latest/index.html) Python library. StatsBomb is a "
                "UK based sports analytics firm and the source of data for a lot of companies in the field of sports "
                "analytics. Further information about the StatsBomb data is provided in the [StatsBomb Open Data "
                "GitHub repository](https://github.com/statsbomb/open-data). The data dictionary for the events data, "
                "which is loaded and used for the analysis, can be found "
                "[here](https://github.com/statsbomb/open-data/blob/master/doc/Open%20Data%20Events%20v4.0.0.pdf).")

    st.markdown("To run this dashboard locally, navigate to the directory the file is located in the terminal and run "
                "the command `streamlit run app.py`.")
