# -*- coding: utf-8 -*-
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
    return f'{split_list[0]} {split_list[1]}'

reddit = praw.Reddit(user_agent='Subreddit Playlist Creator (by /u/malcolm_exe)', client_id='kVTqgt1Y9v8dYQ',client_secret='M3Z0i5NFb8-RpOLjJXFjRlro9R0',username='malcolm_exe')

#user input for subreddit and timeframe
subreddit = reddit.subreddit(input('What subreddit? /r/: '))
while True:
    timeframe = input('What timeframe? Top of [a]ll, [d]ay, [h]our, [m]onth, [w]eek, or [y]ear?')
    if timeframe in ('a','d','h','m','w','y'):
        break

#create list of links, filters by '-' to indicate song title
songs = []
for submission in subreddit.top(time_filter=reddit_timeframes[timeframe],limit=500):
    if '-' in submission.title:
        song_string = song_stringer(submission.title)
        songs.append(song_string)
        
#load configuration
config = configparser.ConfigParser()
config.read('mylogin.ini')

#scope and username
scope = 'playlist-modify-public'
username = config['login']['username']
        
#token
token = util.prompt_for_user_token(username,scope=scope,client_id=config['login']['client_id'],client_secret=config['login']['client_secret'],redirect_uri=config['login']['redirect_uri'])

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    
#create list of playlist ids
    search_queries = []
    for song in songs:
        result = sp.search(song, limit=1, offset=0, type='track')
        if result['tracks']['total'] > 0:
            for r in result['tracks']['items']:
                if(len(search_queries)<100):
#100 limits the playlists to max 100 
                    search_queries.append(r['id'])
                    
#clear all occurences before adding track ids
    existing_tracks = sp.user_playlist_tracks(token, config['login']['playlist_id'])
    present_tracks = []
    for i in existing_tracks['items']:
        present_tracks.append(i['track']['id'])
    sp.user_playlist_remove_all_occurrences_of_tracks(username, config['login']['playlist_id'], present_tracks)

#remove any duplicates from playlist list
    search_queries = set(search_queries)
    search_queries = list(search_queries)

#add trackids
    results = sp.user_playlist_add_tracks(username, config['login']['playlist_id'], search_queries)



#TO-DO
#This needs to do a few things differently
#1. It'd be easier to search on reddit and return top tracks that way
#2. Extract track ids from links instead
#3. Update the description each time ran with time, date, subreddit, time