# -*- coding: utf-8 -*-
"""
Subreddit Playlist Creator
"""

import praw
import spotipy
import spotipy.util as util
import configparser

def match_songtitle(title):
    """
    Find links with 'Artist - Song Title'
    returns a tuple with ('artist','title')
    """
    split_list = title.split('-')
    if 'FRESH' in split_list[0]:
        bracketsplit = split_list[0].split(']')
        split_list[0] = bracketsplit[1]
    return (split_list[0], split_list[1])

reddit = praw.Reddit(user_agent='Subreddit Playlist Creator (by /u/malcolm_exe)', client_id='kVTqgt1Y9v8dYQ',client_secret='M3Z0i5NFb8-RpOLjJXFjRlro9R0',username='malcolm_exe')

#user input for subreddit
subreddit = reddit.subreddit(input('What subreddit? /r/: '))

#create list of links, filters by '-' to indicate song title
songs = []
for submission in subreddit.top(time_filter='year',limit=500):
    if '-' in submission.title:
        song_string = match_songtitle(submission.title)
        song_string = f'{song_string[0]} {song_string[1]}'
        songs.append(song_string)
#to-do: 1. pull trackid's from spotify
#2. add 3 first tracks for albums
        
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
#1. X have it clear everytime you run script. DONE
#2. X remove duplicates before adding DONE
#3. X more refined search DONE 
#4. X user input for subreddit DONE
#5. have it pull the track id if it's a spotify link
#6. learn git and refine this?