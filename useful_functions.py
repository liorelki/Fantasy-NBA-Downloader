"""
Useful functions:

# Create a file with the authentication information:
creds = {
    'consumer_key': my_key,
    'consumer_secret': my_secret
}

with open('oauth2.json', 'w') as f:
    f.write(json.dumps(creds))

# List of all league ids I have ever played in:
game = yfa.Game(oauth, 'nba')
print(game.league_ids())

List of all teams in certain league:
lg = yfa.League(oauth, '428.l.8925')
print(lg.teams())
for key in lg.teams().keys():
    print(lg.teams()[key]['name'])

Get team roster stats:
lg = yfa.League(oauth, '428.l.8925')
my_team = yfa.Team(oauth, '428.l.8925.t.8')
print(my_team.roster())
print(lg.player_stats(my_team.roster()[0]['player_id'], req_type='lastmonth'))

"""

import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerNextNGames
from nba_api.stats.endpoints import TeamGameLog
from nba_api.stats.endpoints import scheduleleaguev2
from nba_api.stats.static import teams
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
import datetime
import plotly.express as px
import json

from streamlit import header

# List of all league ids I have ever played in:
# oauth = OAuth2(None, None, from_file='oauth2.json')
# game = yfa.Game(oauth, 'nba')
# print(game.league_ids())
#
# # List of all teams in specific league, and their IDs:
# lg = yfa.League(oauth, '466.l.21709')
# print(lg.teams())
# for key in lg.teams().keys():
#     print(lg.teams()[key]['name'] + ' - ' + key)

# players_list = players.get_players()
# # print(players_list[0])
#
# # Get game log of specific player
# # player = "Deni Avdija"
# # player = "Jalen Williams"
# # player = "Donovan Clingan"
# # player = 'Isaiah Collier'
# # player_debug = [x for x in players_list if x['full_name']==player]
# # player_id = [x for x in players_list if x['full_name']==player][0]['id']
# # print(player_debug)
# # game_log = playergamelog.PlayerGameLog(player_id=player_id, season='2024')
# # print(game_log.get_data_frames()[0].head(15))
# # print(game_log.get_data_frames()[0].head(15).columns)
# # print(f'{player}:')
# # stat = 'TOV'
# # print(game_log.get_data_frames()[0][stat].mean())
# # print(game_log.get_data_frames()[0][stat].std())
# # bar = px.histogram(game_log.get_data_frames()[0], x=stat, nbins=20, histnorm='probability' )
# # bar.show()
# # bar2 = px.histogram(game_log.get_data_frames()[0], x=stat, nbins=20, cumulative=True, histnorm='probability')
# # bar2.show()
#
# # player_id = [x for x in players_list if x['full_name']==player][0]['id']
# # game_log = playergamelog.PlayerGameLog(player_id=player_id, season='2024')
#
# # Get schedule of specific team:
#
# list_teams = teams.get_teams()
# # print(list_teams)
# team = 'Los Angeles Lakers'
# team_id = [x['id'] for x in list_teams if x['full_name']==team][0]
# print(team_id)
#
schedule = scheduleleaguev2.ScheduleLeagueV2().get_data_frames()[0]

print(schedule[['homeTeam_teamName','awayTeam_teamName','gameDate']])
#
schedule[['homeTeam_teamName','homeTeam_teamId' ,'awayTeam_teamName','awayTeam_teamId','gameDate']].to_json('schedule.json',orient='records')
# with open('schedule.json', 'r') as f:
#     json_schedule = json.load(f)
#     df_schedule = pd.DataFrame(json_schedule)
#     print(df_schedule)
# # print(df_schedule[(df_schedule['homeTeam_teamName'] == team) | (df_schedule['awayTeam_teamName'] == team)])
# df_schedule.gameDate = pd.to_datetime(df_schedule.gameDate)
# print(df_schedule[(df_schedule['homeTeam_teamId'] == team_id) | (df_schedule['awayTeam_teamId'] == team_id)])
# df_schedule_team = df_schedule[(df_schedule['homeTeam_teamId'] == team_id) | (df_schedule['awayTeam_teamId'] == team_id)]
# print(len(df_schedule_team[(df_schedule_team.gameDate>"2025-03-16") & (df_schedule_team.gameDate<"2025-03-24")]))
# # df = df[df<"2025-03-24"]
# # print(df)
# # print(len(df))
# # df = schedule.query(f'homeTeam_teamId=={team_id} or awayTeam_teamId=={team_id}')[['homeTeam_teamName','awayTeam_teamName','gameDate','homeTeam_score']]
# # df = pd.to_datetime(df.gameDate)
# # df = df[df>"2025-03-16"]
# # df = df[df<"2025-03-24"]
# # print(df)
# # print(len(df))
#
# # print(schedule.homeTeam_teamName)
#
# # print(team_games)
#
# # dict_2 = PlayerNextNGames(player_id=player_id).get_data_frames()[0].GAME_DATE
# # # print(game_log.get_data_frames()[0].head(15))
# # print('Jones:')
# # print(game_log.get_data_frames()[0].head(15).STL.mean())
# # print(game_log.get_data_frames()[0].head(15).STL.std())
# # Get remaining games of specific player
# # with open('Player name translator.json',mode='r', encoding='utf-8') as f:
# #     dict=json.load(f)
# #     print(dict)
# #
#
#
# #
# # player_id = [x for x in players_list if x['full_name']==player][0]['id']
# # dict_2 = PlayerNextNGames(player_id=player_id).get_data_frames()[0].GAME_DATE
# # dict_2 = pd.to_datetime(dict_2)
# # print(dict_2[dict_2<'2025-03-03'])
#
# # Get the end date of a current week:
# # lg.matchups(week=1)
# # matchup_meta = lg.matchups(week=1)['fantasy_content']['league'][LEAGUE_DATA]['scoreboard'][SCOREBOARD_DATA]['matchups']
# # end_date = matchup_meta[matchup_index]['matchup']['week_end']


