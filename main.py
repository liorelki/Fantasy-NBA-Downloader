from symbol import continue_stmt

from yahoo_oauth import OAuth2 # version - 2.0.0
import yahoo_fantasy_api as yfa # version - 2.8.0
import requests  # version - 2.31.0
import json
import plotly.express as px # version - 5.17.0
import streamlit as st # version - 1.27.2
import pandas as pd # version - 1.3.0
import numpy as np # version - 1.25.2
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerNextNGames
from nba_api.stats.static import teams
from datetime import datetime
from auto_update import *


# Used only to create the credential files:
# with open('oauth2.json', 'w') as f:
#     f.write(json.dumps(creds))

app_id = 'otqwlUo0'

oauth = OAuth2(None, None, from_file='oauth2.json')

# 2025 League IDs:
LEAGUE_IDS = {
    'LOJP': '466.l.3197',
    'IFSL': '466.l.160865',
    'The Sixth Man': '466.l.2705',
    'Hard Cap': '466.l.21709'
}

# 2025 Team IDs:
TEAM_IDS = {
    'LOJP': '466.l.3197.t.5',
    'IFSL': '466.l.160865.t.7',
    'The Sixth Man': '466.l.2705.t.14',
    'Hard Cap': '466.l.21709.t.3'
}

# Relevant fields
# FIELDS_YFA - fields for players data from Yahoo
# FIELDS_SHEET - fields in Google sheets to download player data
# FIELDS_TEAM - categories of the leagues
FIELDS_YFA = ['name', 'GP', 'FG%', 'FT%', 'FGM', 'FGA', 'FTM', 'FTA', '3PTM', 'PTS', 'REB', 'AST', 'ST', 'BLK', 'TO']
FIELDS_SHEET = ['player', 'gp', 'fg', 'ft', 'fgm', 'fga', 'ftm', 'fta', 'tript', 'pts', 'reb', 'ast', 'stl', 'blk',
                'to']
FIELDS_TEAM = ['FG', 'FT', '3PT', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']

# Static data:
LEAGUE_DATA = 1
SCOREBOARD_DATA = '0'
MATCHUP_TEAMS = '0'
TEAM_DATA = 0  # 0 is for team data and getting the team name under index 2

# Google sheet endpoints:

try:
    with open('sheet_details.json', mode='r') as f:
        data = json.load(f)
        headers = data['headers']
        sheet_endpoint = data['sheet_endpoint']
except FileNotFoundError:
        print('No sheet_details.json')




st.set_page_config(page_title='NBA Fantasy Analyser',
                       page_icon=None,
                       layout="wide",
                       initial_sidebar_state="auto",
                       menu_items=None)

# Functions used to get player stats:


def yfa_my_team_stats(lg, search_input=None, team=None, request='lastmonth', games=True):
    # Patch league stats - no static ids for nba
    lg._get_static_id_map = lambda _x: {
        0: "GP",
        3: "FGA",
        4: "FGM",
        6: "FTA",
        7: "FTM"
    }

    if search_input == 'Team' or search_input == 'All teams':
        my_team = yfa.Team(oauth, team)
        roster = my_team.roster()
    elif search_input == 'FA':
        my_team = lg.waivers()
        my_team.extend(lg.free_agents(position='util'))
        # roster = my_team[:200]
        roster = [element for element in my_team if element['percent_owned'] > 0]
    else:
        player_response = lg.player_details(search_input)
        # print(player_response)
        if not player_response:
            print(f"Typo in player's name: {search_input}")
            return
        else:
            roster = player_response
            # print(player_response)
    # print(f'Roster is : {roster}')
    for player in roster:
        # player_name = player['name']
        # print(player)
        get_player_stats(player, lg, request, proj=games)

    done = {'player_id': 0, 'name': 'Done'}
    get_player_stats(done, lg, request,proj=False)
    return


def get_player_stats(player, lg, request, proj=True):
    # test=False
    # if test:
    if player['name'] == 'Done':
        player_stats = {'player': 'Done'}
    else:
        if request is not "weighted":
            all_stats = lg.player_stats(player['player_id'], req_type=request)[0]
            all_stats = {k: (0 if v == "-" else v) for k, v in all_stats.items()}
            # print(all_stats)
            player_stats = {FIELDS_SHEET[FIELDS_YFA.index(key)]: all_stats[key] for key in FIELDS_YFA[:4]}
            try:
                player_stats.update(
                    {FIELDS_SHEET[FIELDS_YFA.index(key)]: round(all_stats[key] / all_stats['GP'], 1) for key in FIELDS_YFA[4:]})
            except ZeroDivisionError:
                player_stats.update({FIELDS_SHEET[FIELDS_YFA.index(key)]: round(0, 1) for key in FIELDS_YFA[2:]})
            else:
                print('ok')
                # print(player_stats)
        else:
            monthly_all_stats = lg.player_stats(player['player_id'], req_type='lastmonth')[0]
            weekly_all_stats = lg.player_stats(player['player_id'], req_type='lastweek')[0]
            # print(monthly_all_stats)
            # print(weekly_all_stats)
            monthly_all_stats = {k: (0 if v == "-" else v) for k, v in monthly_all_stats.items()}
            weekly_all_stats = {k: (0 if v == "-" else v) for k, v in weekly_all_stats.items()}

            if weekly_all_stats['GP'] == 0:
                alpha = 0
                weekly_all_stats['GP'] = 0.1
            else:
                alpha = 0.6

            player_stats = {FIELDS_SHEET[FIELDS_YFA.index(key)]: monthly_all_stats[key] for key in FIELDS_YFA[:2]}
            player_stats.update(
                {FIELDS_SHEET[FIELDS_YFA.index(key)]: (1-alpha)*monthly_all_stats[key]+
                                                      alpha*weekly_all_stats[key] for key in FIELDS_YFA[2:4]})
            try:
                player_stats.update(
                    {FIELDS_SHEET[FIELDS_YFA.index(key)]:
                         round((1-alpha)*(monthly_all_stats[key]/monthly_all_stats['GP'])+
                               alpha*(weekly_all_stats[key]/weekly_all_stats['GP']), 1) for key in FIELDS_YFA[4:]})
            except ZeroDivisionError:
                player_stats.update({FIELDS_SHEET[FIELDS_YFA.index(key)]: round(0, 1) for key in FIELDS_YFA[2:]})
            else:
                print('ok')
                # print(player_stats)

        if proj:
            lg.matchups(week=lg.current_week())
            matchup_meta = lg.matchups(week=lg.current_week())['fantasy_content']['league'][LEAGUE_DATA]['scoreboard'][
                SCOREBOARD_DATA]['matchups']
            end_date = matchup_meta['0']['matchup']['week_end']
            start_date = datetime.today().strftime('%Y-%m-%d')

            list_teams = teams.get_teams()

            player_response = lg.player_details(int(player['player_id']))[0]
            # print(player_response)

            team_name = player_response['editorial_team_full_name']
            if team_name == "LA Clippers":
                team_name = "Los Angeles Clippers"
            team_id = [x['id'] for x in list_teams if x['full_name'] == team_name][0]

            with open('schedule.json', 'r') as f:
                json_schedule = json.load(f)
                df_schedule = pd.DataFrame(json_schedule)

            df_schedule.gameDate = pd.to_datetime(df_schedule.gameDate)
            df_schedule_team = df_schedule[
                (df_schedule['homeTeam_teamId'] == team_id) | (df_schedule['awayTeam_teamId'] == team_id)]

            player_stats['gp'] = float(len(df_schedule_team[
                          (df_schedule_team.gameDate >= start_date) & (df_schedule_team.gameDate <= end_date)]))

    body = {'myteamstat': player_stats}
    response = requests.post(url=sheet_endpoint, json=body, headers=headers)
    print(response)

    return


# Functions used to get team stats:
# get_weekly_stats - get team stats in categories from a certain week
# get_yearly stats - go over all the weeks up until current week, get data and save it to file
# save_year_data - save data to JSON file of the league


def get_weekly_stats(week, lg):
    weekly_stats = {}
    average_weekly_stats = {}
    matchup_meta = lg.matchups(week=week)['fantasy_content']['league'][LEAGUE_DATA]['scoreboard'][SCOREBOARD_DATA][
        'matchups']
    # print(f'\n{matchup_meta}\n')
    for matchup_index in list(matchup_meta.keys())[:-1]:
        for matchup_team in [0, 1]:
            team_name = matchup_meta[matchup_index]['matchup'][MATCHUP_TEAMS]['teams'][str(matchup_team)]['team'][
                TEAM_DATA][2]['name']
            team_stats_dict = matchup_meta[matchup_index]['matchup'][MATCHUP_TEAMS]['teams'][str(matchup_team)]['team'][
                TEAM_DATA + 1]['team_stats']['stats']
            games_completed = int(
                matchup_meta[matchup_index]['matchup'][MATCHUP_TEAMS]['teams'][str(matchup_team)]['team'][
                    TEAM_DATA + 1]['team_remaining_games']['total']['completed_games'])
            weekly_stats[team_name] = {
                "FGM": team_stats_dict[0]['stat']['value'].split('/')[0],
                "FGA": team_stats_dict[0]['stat']['value'].split('/')[1],
                "FG": team_stats_dict[1]['stat']['value'],
                "FTM": team_stats_dict[2]['stat']['value'].split('/')[0],
                "FTA": team_stats_dict[2]['stat']['value'].split('/')[1],
                "FT": team_stats_dict[3]['stat']['value'],
                "3PT": team_stats_dict[4]['stat']['value'],
                "PTS": team_stats_dict[5]['stat']['value'],
                "REB": team_stats_dict[6]['stat']['value'],
                "AST": team_stats_dict[7]['stat']['value'],
                "STL": team_stats_dict[8]['stat']['value'],
                "BLK": team_stats_dict[9]['stat']['value'],
                "TO": team_stats_dict[10]['stat']['value'],
            }
    # print(weekly_stats)

    return weekly_stats


def get_yearly_stats(lg, league_name):
    current_week = lg.current_week()
    # weeks = list(range(1, current_week))
    weeks = list(range(1, current_week+1))
    # print(weeks)
    year_stats = {}
    for week in weeks:
        week_stats = get_weekly_stats(week=week, lg=lg)
        # print(week_stats)
        year_stats[week] = week_stats
        save_year_data(week=week, lg=lg, data_to_save=week_stats, league=league_name)

    # print(year_stats)
    return year_stats


def save_year_data(week, lg, data_to_save, league='LOJP'):
    # print(league)
    try:
        with open(f'{league}.json', mode='r') as f:
            data = json.load(f)
            try:
                print(data[str(week)])
            except KeyError:
                data.update({week: data_to_save})
            else:
                data[str(week)] = data_to_save
    except FileNotFoundError:
        with open(f'{league}.json', mode='w') as f:
            data_to_dump = {str(week): data_to_save}
            json.dump(data_to_dump, f, indent=4)
    else:
        with open(f'{league}.json', mode='w') as f:
            json.dump(data, f, indent=4)


# Functions used to plot team stats:
# highlight_top_bottom - used to highlight the top and bottom 4 in each category in the table
# plot_team_stats - used to plot the tables and graphs for each category


def highlight_top_bottom(s):
    is_top = s >= s.nlargest(5).min()
    is_bottom = s <= s.nsmallest(5).max()

    return ['background-color: #B5EAD7' if top else
            'background-color: #FFB3BA' if bottom else
            '' for top, bottom in zip(is_top, is_bottom)]


def plot_teams_stats(lg, league='LOJP'):
    teams_fantasy = pd.DataFrame(lg.teams().values()).name.to_list()
    try:
        with open(f'{league}.json', mode='r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print('File not found. Please get yearly data to create a file')
    else:
        new_df = pd.DataFrame(columns=['week', 'team','FGM', 'FGA', 'FG', 'FTM', 'FTA', 'FT', '3PT', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO'])
        for week in list(data.keys()):
            for team in teams_fantasy:
                new_row = {'week': int(week),
                           'team': team,
                           'FGM': float(data[week][team]['FGM']),
                           'FGA': float(data[week][team]['FGA']),
                           'FG': round(float(data[week][team]['FG']), 3),
                           'FTM': float(data[week][team]['FTM']),
                           'FTA': float(data[week][team]['FTA']),
                           'FT': round(float(data[week][team]['FT']), 3),
                           '3PT': float(data[week][team]['3PT']),
                           'PTS': float(data[week][team]['PTS']),
                           'REB': float(data[week][team]['REB']),
                           'AST': float(data[week][team]['AST']),
                           'STL': float(data[week][team]['STL']),
                           'BLK': float(data[week][team]['BLK']),
                           'TO': float(data[week][team]['TO'])
                           }
                new_df = new_df.append(new_row, ignore_index=True)


        # print(new_df)

        df_last = new_df[new_df['week']==lg.current_week()]

        df_avg = new_df[new_df['week']<lg.current_week()].groupby('team').mean()

        alpha = 0.7
        df_ewm_all = new_df[new_df['week']<lg.current_week()].groupby('team').ewm(alpha=alpha).mean()  # Returns exponential average for each week
        df_ewm_last = df_ewm_all.loc[df_ewm_all['week']==df_ewm_all['week'].max()]  # Get only the last week
        df_ewm_last.reset_index(inplace=True)
        df_ewm_last = df_ewm_last.drop(columns=['level_1', 'week']).set_index('team')

        st.subheader('Current week:', divider='blue')
        width = 1800
        height = 455
        st.dataframe(df_last[['team','FGM', 'FGA', 'FTM', 'FTA', '3PT', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']], width=width, height=height)

        # columns you DO NOT want rounded
        no_round = ['FG', 'FT']  # <-- change these
        # Start with 1-decimal format for all columns
        fmt = {c: "{:.1f}" for c in df_avg.columns}
        # Override FG/FT to have 3 decimals
        for c in no_round:
            fmt[c] = "{:.3f}"

        st.subheader('Season average:', divider='blue')
        width = 1800
        height = 455
        st.dataframe(df_avg[['FG', 'FT', '3PT', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']].style.apply(highlight_top_bottom).format(fmt), width=width, height=height)
        # st.dataframe(df_avg, width=width, height=height)

        percentile = pd.DataFrame({field: [np.quantile(df_avg[field], 0.75)] for field in FIELDS_TEAM})
        st.dataframe(percentile.style.format(fmt), width=width)
        # st.write(f"top 75%: {percentile}")

        st.subheader(f'Moving exponential average (alpha={alpha}):', divider='blue')
        # st.dataframe(df_avg_last_5.style.apply(highlight_top_bottom), width=width, height=height)
        st.dataframe(df_ewm_last[['FG', 'FT', '3PT', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO']].style.apply(highlight_top_bottom).format(fmt), width=width, height=height)

        color_plot = px.colors.qualitative.Dark24

        for field in FIELDS_TEAM:
            fig = px.line(new_df, x='week', y=field, color='team', color_discrete_sequence=color_plot)
            fig.update_layout(width=width, height=1.5*height)
            st.subheader(f'{field}:', divider='blue')
            st.plotly_chart(fig)


if __name__ == '__main__':
    # League section:
    st.subheader('League Selection:', divider='red')
    league_name = st.radio(label='Select League:',
                           options=list(LEAGUE_IDS.keys()))
    lgy = yfa.League(oauth, LEAGUE_IDS[league_name])


    # Save notes to file and update them:
    try:
        with open(f'{league_name}_notes.txt', mode='r') as f:
            load_text = f.read()
            size = len(load_text.splitlines())
    except FileNotFoundError:
        with open(f'{league_name}_notes.txt', mode='w') as f:
            load_text = 'Empty'

    text = st.text_area(
        label='Notes:',
        value=f'{load_text}',
        height=(size+1)*40
    )

    if st.button(label='Save notes'):
        with open(f'{league_name}_notes.txt', mode='w') as f:
            f.write(text)


    # Action section:
    st.subheader('Actions', divider='red')
    left, right = st.columns(2)

    # Player data:
    search_type = right.radio(label='Which stats to get?',
                              options=['FA', 'Team', 'specific_player', 'All teams'])

    player_enable = True
    if search_type == 'specific_player':
        player_enable = False

    team_enable = True
    if search_type == 'Team':
        team_enable = False

    db_teams = pd.DataFrame(lgy.teams().values())
    db_teams.set_index('name', inplace=True)

    team_input = right.selectbox('Team',
                                 db_teams.index.to_list(),
                                 index=0,
                                 disabled=team_enable,
                                 label_visibility='visible')

    specific_player = right.text_input(label='Player Name',
                                       value=None,
                                       disabled=player_enable)

    timeframe = right.radio(label='Which timeframe?',
                            options=['lastmonth', 'lastweek', 'season','weighted'])


    remaining_games = right.checkbox(label='Remaining Games',value=False)

    if right.button(label='Get Player Stats'):
        if search_type == 'specific_player':
            search = specific_player
            teams_pick = [None]
        else:
            if search_type == 'All teams':
                teams_pick = db_teams.index.to_list()
            else:
                teams_pick = [team_input]
            search = search_type

        for team in teams_pick:
            if team is None:
                specific_team_key = None
            else:
                specific_team_key = db_teams.loc[team]['team_key']
            yfa_my_team_stats(lgy, search_input=search, team=specific_team_key, request=timeframe, games=remaining_games)

    right.write(
        'Link to "downloaded player stats":')
    right.write(
        'https://docs.google.com/spreadsheets/d/1rSekvvfNNiEIMT0PN4nQaUBYKxbxzm4roA4X2ZJ3Cu4/edit?gid=211814430#gid=211814430')

    right.write(
        'Link to "My team" analysis:')
    right.write(
        'https://docs.google.com/spreadsheets/d/1eeoBN5rIW3iOoIs3nHkbKiUQzPluR0H5yRmn6IerkAc/edit?gid=1824273107#gid=1824273107')

    #  Team data:
    left.write(f'Current week: {lgy.current_week()}')
    timeframe = left.radio(label='Select timeframe:',
                           options=['Specific week', 'All year'])

    week_enable = True
    if timeframe == 'Specific week':
        week_enable = False

    requested_week = left.number_input(label='Week:',
                                       value=lgy.current_week(),
                                       step=1,
                                       disabled=week_enable)

    if left.button(label='Update data'):
        if timeframe == 'All year':
            get_yearly_stats(lgy, league_name)
        else:
            week_stats = get_weekly_stats(week=requested_week, lg=lgy)
            save_year_data(week=requested_week, lg=lgy, data_to_save=week_stats, league=league_name)

    if check_if_updated():
        print('updated')
        pass
    else:
        print('not updated')
        # update all leagues
        for league_name_u in LEAGUE_IDS.keys():
            lgy_u = yfa.League(oauth, LEAGUE_IDS[league_name_u])

            if check_if_week_passed():
                # if this is a new week then update all weeks
                get_yearly_stats(lgy_u, league_name_u)
            else:
                # if we are in the same week, just different day, update only this week
                week_stats = get_weekly_stats(week=lgy.current_week(), lg=lgy_u)
                save_year_data(week=lgy.current_week(), lg=lgy_u, data_to_save=week_stats, league=league_name_u)

        # after the updates, update the saved date in the file
        update_date()

    # if left.button(label='Plot Team Stats'):
    #     plot_teams_stats(lgy, league_name)
    # yfa_my_team_stats(lgy, search_input='Sabonis', team=None, request='weighted', games=True)

    plot_teams_stats(lgy, league_name)
