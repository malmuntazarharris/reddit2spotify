"""
Subreddit Playlist Creator
"""

import praw
import spotipy
import spotipy.util as util
import configparser


reddit_timeframes = {
        'a':'all',
        'd':'day',
        'h':'hour',
        'm':'month',
        'w':'week',
        'y':'year',
        }

def song_stringer(title):
    """
    Find links with 'Artist - Song Title'
    returns a string with song and artist
    """
    split_list = title.split('-')
    if 'FRESH' in split_list[0]:
        bracketsplit = split_list[0].split(']')
        split_list[0] = bracketsplit[1]
    try:
        return f'{split_list[0]} {split_list[1]}'
    except: 
        return f'{split_list[0]}'
        
#load configuration
config = configparser.ConfigParser()
config.read('mylogin.ini')
        
#reddit token
reddit = praw.Reddit(user_agent=config['reddit']['user_agent'], client_id=config['reddit']['client_id'], client_secret=config['reddit']['client_secret'],username=config['reddit']['username'])

#user input for subreddit and timeframe
subreddit = reddit.subreddit(input('What subreddit? /r/: '))
while True:
    timeframe = input('What timeframe? Top of [a]ll, [d]ay, [h]our, [m]onth, [w]eek, or [y]ear?')
    if timeframe in ('a','d','h','m','w','y'):
        break

#create list of search items and directly pulled track ids
to_search = []
track_ids = []
for submission in subreddit.top(time_filter=reddit_timeframes[timeframe],limit=500):
    if "FRESH" in submission.title:
        if "open.spotify.com/track/" in submission.url:
            track_ids.append(submission.url[31:53])
        else:
            song_string = song_stringer(submission.title)
            to_search.append(song_string)
        

#Spotify scope and username
scope = 'playlist-modify-public'
username = config['spotify']['username']
        
#Spotify token
token = util.prompt_for_user_token(username,scope=scope,client_id=config['spotify']['client_id'],client_secret=config['spotify']['client_secret'],redirect_uri=config['spotify']['redirect_uri'])

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    
#add searches to list of track ids
    for song in to_search:
        result = sp.search(song, limit=1, offset=0, type='track')
        if result['tracks']['total'] > 0:
            for r in result['tracks']['items']:
                if(len(track_ids)<100):
    #100 limits the playlists to max 100 
                    track_ids.append(r['id'])
                    
#clear all occurences before adding track ids
    existing_tracks = sp.user_playlist_tracks(token, config['spotify']['playlist_id'])
    present_tracks = []
    for i in existing_tracks['items']:
        present_tracks.append(i['track']['id'])
    sp.user_playlist_remove_all_occurrences_of_tracks(username, config['spotify']['playlist_id'], present_tracks)

#remove any duplicates from playlist list
    track_ids = list(set(track_ids))

#add trackids
    results = sp.user_playlist_add_tracks(username, config['spotify']['playlist_id'], track_ids)