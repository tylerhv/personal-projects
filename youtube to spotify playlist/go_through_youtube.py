import urllib.request
import json
import re
from apiclient.discovery import build
import requests
import spotipy
import os
import sys
import webbrowser
import spotipy.util as util
import json

#global variables
user = 'user'
playlist_scope= 'playlist-modify-public'
playlistid = 'playlist_id'
clientID = "client_id"
secretID = 'client_secret'
redirectUri = 'https://www.google.com/'

#setting environment variables
def setup():
    api_key = 'youtube_api'
    return build('youtube', 'v3', developerKey=api_key)

#searching for videos
def grab_videos(youtube):
    req = youtube.search().list(q='"Weekly Track Roundup:"', part='snippet', publishedAfter='2022-01-05T00:00:00Z', maxResults=2, order = 'date', type='video' )
    res = req.execute() #finds all videos with "Weekly Track Roundup" in it
    video_id_list = []

    for item in res['items']:#adds a list of video id's
        video_id_list.append((item['id']['videoId']))
    return video_id_list

#writing the description FORMATTED!!!!
def get_video_description(youtube, video_id_list):     
    for i in video_id_list:
        a = youtube.videos().list(id=i, part='snippet')
        results = a.execute()
        
        for result in results.get('items', []):
            desc_text = open('description.txt', 'w')
            desc_text.write(result['snippet']['description'])
            desc_text.close()


def best_track_only():
    #setting the beginning and end of "best tracks this week" and "meh"
    pattern_start = re.compile(r'!!!BEST TRACKS THIS WEEK!!!')
    desc_text = open('description.txt', 'r')
    desc_var = desc_text.read()
    matches_start = re.search(pattern_start, desc_var)
    starting_pos = matches_start.end()

    pattern_end = re.compile(r'...meh...')
    matches_end = re.search(pattern_end, desc_var)
    ending_pos = matches_end.start()
    desc_text.close()



    songs_only = ''

    for i in range(starting_pos, ending_pos): #this will make it so that all the songs are in a variable
        songs_only = songs_only + desc_var[i]
        
    #puts only the lines listed in the "BEST TRACKS OF THE WEEK" section to a text file, in order to remove the HTML links
    print(songs_only)
    desc_text = open('description.txt', 'w') 
    desc_text.write(songs_only)
    desc_text.close()

    #gets all of the lines from the document
    desc_text = open("description.txt", "r")
    lines = desc_text.readlines()
    desc_text.close()
    print(lines)

    #gets rid of all of the HTML links in the description
    desc_text = open("description.txt", "w")
    for line in lines:
        if line.find("https") == -1:
            desc_text.write(line)
    desc_text.close()

#authorizing spotify access to API
def spotify_auth():
    redirectUri = 'https://www.google.com/'

    oauth_object = spotipy.SpotifyOAuth(client_id = clientID, client_secret = secretID, redirect_uri = redirectUri, scope=playlist_scope)
    token_dict = oauth_object.get_access_token()
    token = token_dict['access_token']
    return spotipy.Spotify(auth = token)

#seperates artist from the name of the song. We will use the artist name and song name to search for the track on spotify later
def seperating_artist_song():
    desc_text = open('description.txt', 'r')
    artist_name = []
    song_name = []

    lines = desc_text.readlines()
    for line in lines:
        seperator = line.find('-')
        if seperator == -1:
            continue
        else:
            artist_name.append(line[:seperator-1])
            song_name.append(line[seperator+2:-1])
    desc_text.close()
    return(artist_name,song_name)

#using the artist name and song name, we get the song id on spotify. adds and returns a list of those trackid's. If a song is not found on spotify, we skip it
def get_list_ids(sp, artist_name, song_name):
    list_trackid = []
    for i in range(len(artist_name)):
        track_id = sp.search(q='artist:' + artist_name[i] + ' track:' + song_name[i], type='track')
        try:
            list_trackid.append(track_id['tracks']['items'][0]['id'])
        except:
            continue
    return list_trackid

#using the track ids, adds tracks to spotify
def add_tracks_to_spotify(sp, list_trackid):
    sp.user_playlist_add_tracks(user, playlist_id=playlistid, tracks = list_trackid)
    print("Done!")

#main   
def main():
    yt = setup()
    video_ids = grab_videos(yt)
    print(video_ids)
    get_video_description(yt, video_ids)
    best_track_only()
    spotify_obj = spotify_auth()
    artist_and_songs = seperating_artist_song()
    track_ids = get_list_ids(spotify_obj, artist_and_songs[0], artist_and_songs[1])
    add_tracks_to_spotify(spotify_obj, track_ids)
    
main()
    

    

