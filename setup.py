import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from nba_api.stats.endpoints import scheduleleaguev2

# List of all league ids I have ever played in:
oauth = OAuth2(None, None, from_file='oauth2.json')
game = yfa.Game(oauth, 'nba')
print(game.league_ids())

# List of all teams in specific league, and their IDs:
lg = yfa.League(oauth, '466.l.21709')
print(lg.teams())
for key in lg.teams().keys():
    print(lg.teams()[key]['name'] + ' - ' + key)

# Download schedule of season to JSON file:
schedule = scheduleleaguev2.ScheduleLeagueV2().get_data_frames()[0]
print(schedule[['homeTeam_teamName','awayTeam_teamName','gameDate']])
schedule[['homeTeam_teamName','homeTeam_teamId' ,'awayTeam_teamName','awayTeam_teamId','gameDate']].to_json('schedule.json',orient='records')