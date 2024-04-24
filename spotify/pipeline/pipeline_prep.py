import json
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import glob
import pytz
from dotenv import load_dotenv
import streamlit as st

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
print(client_id, client_secret)

os.getcwd()


# Importing data
stream_1 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2015-2017_0.json')
stream_2 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2017-2018_1.json')
stream_3 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2018_2.json')
stream_4 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2018-2019_3.json')
stream_5 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2019-2020_4.json')
stream_6 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2020-2021_5.json')
stream_7 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2021-2022_6.json')
stream_8 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2022-2023_7.json')
stream_9 = pd.read_json('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/Extended History/Streaming_History_Audio_2023-2024_8.json')

stream_data = pd.concat([stream_1,stream_2,stream_3,stream_4,stream_5,stream_6,stream_7,stream_8,stream_9])
#'ts', 'username', 'platform', 'ms_played', 'conn_country', 'ip_addr_decrypted', 'user_agent_decrypted',
# 'master_metadata_track_name', 'master_metadata_album_artist_name',
# 'master_metadata_album_album_name', 'spotify_track_uri', 'episode_name','episode_show_name', 'spotify_episode_uri', 'reason_start',
# 'reason_end', 'shuffle', 'skipped', 'offline', 'offline_timestamp','incognito_mode'



spotify_tracks = pd.read_csv('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/data/track_info.csv') 
#'track_id', 'artists', 'album_name', 'track_name','popularity', 'duration_ms', 'explicit', 'danceability', 'energy',
#'key', 'loudness', 'mode', 'speechiness', 'acousticness','instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature',
#'track_genre'

f = open('C:/Users/micev/OneDrive/Desktop/Pepe/Personal Projects/Environment Test/spotify/data/Spotify Account Data/YourLibrary.json', encoding= 'utf-8')
data= json.load(f)
my_lib = pd.json_normalize(data['tracks'])
#'artist', 'album', 'track', 'uri'

utc = pytz.timezone('UTC')
est = pytz.timezone('US/Eastern')


# Data Cleaning and Manipulation
my_lib['uri'] = my_lib['uri'].str.replace('spotify:track:','%Y-%m-%d %H:%M')

stream_data['ts'] = stream_data['ts'].str.replace('T',' ').str.replace('Z','')
stream_data['ts'] = pd.to_datetime(stream_data['ts'], format = '%Y-%m-%d %H:%M:%S').dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
stream_data['mPlayed'] = round(stream_data['ms_played'] / 60000.0 , 2)
stream_data['startTime'] = stream_data['ts'] - pd.to_timedelta(stream_data['mPlayed'], unit = 'm')
stream_data['year'] = stream_data['ts'].dt.year
stream_data['month'] = stream_data['ts'].dt.month
stream_data['day'] = stream_data['ts'].dt.day

# Joining data together
my_lib_genre = my_lib.merge(spotify_tracks, how = 'left', left_on ='uri', right_on='track_id', suffixes=('_lib','_spotify'))

stream_data.describe()
# Data Wrangling
avg_musicality_by_genre = spotify_tracks.groupby('track_genre')[['danceability','energy','loudness','speechiness','acousticness','instrumentalness']].agg(np.mean)


top_artists_listened = pd.DataFrame(stream_data.groupby(['year','master_metadata_album_artist_name'])['mPlayed'].agg(np.sum)).reset_index().sort_values('mPlayed',ascending=False)

top_5_artists_by_year = top_artists_listened.groupby(['year','master_metadata_album_artist_name'])['mPlayed']

pivot = stream_data.pivot_table(values = 'mPlayed', index=['year','master_metadata_album_artist_name'])
seconds_listened_by_year = stream_data.pivot_table(values = 'mPlayed', index=['year'], aggfunc= np.sum)

#   Box Plot of 
fig = px.box(spotify_tracks, x = 'track_genre', y="loudness",color_discrete_sequence= ['#1DB954']*len(stream_data))


mom_listened = px.bar(stream_data, x='year', y= 'mPlayed', color_discrete_sequence= ['#1DB954']*len(stream_data))



# Streamlit App Configuration

st.title("Hello World")
st.write('This is a test text')
st.metric('my metric', 40,2)
st.bar_chart(stream_data, x='year', y= 'mPlayed')
st.line_chart()

st.sidebar.header('Choose your filter: ')
year_filter = st.sidebar.multiselect('Pick your year',stream_data['year'].unique())
artist_filter = st.sidebar.multiselect('Pick your artist',stream_data['master_metadata_album_artist_name'].unique())
if not year_filter and not artist_filter:
    filtered_df = stream_data
elif year_filter and not artist_filter:
    filtered_df = stream_data[stream_data['year'].isin(year_filter)]
elif not year_filter and artist_filter:
    filtered_df = stream_data[stream_data['master_metadata_album_artist_name'].isin(artist_filter)]
else:
    filtered_df = stream_data[stream_data['year'].isin(year_filter) & stream_data['master_metadata_album_artist_name'].isin(artist_filter)]
    
total_seconds_played = filtered_df.groupby(by = ['year','master_metadata_album_artist_name'], as_index=False)['mPlayed'].agg(np.sum)
print(total_seconds_played)


st.bar_chart(total_seconds_played, x='year',y='mPlayed', color = 'master_metadata_album_artist_name')

#genre_filter = st.sidebar.multiselect('Pick your genre',stream_data[])
print(filtered_df.columns)
