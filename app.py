import pickle
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "e55445565b354e9394d22dde6ca82057"
CLIENT_SECRET = "dbf3e7411c7745ab83e10701877c35f8"

client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def get_spotify_track_url(song_name, artist_name):
    try:
        query = f"track:{song_name} artist:{artist_name}"
        result = sp.search(q=query, type='track', limit=1)
        if result['tracks']['items']:
            return result['tracks']['items'][0]['external_urls']['spotify']
    except Exception as e:
        print("Error fetching track:", e)
    return None

def extract_track_id(spotify_url):
    if isinstance(spotify_url, str) and "track" in spotify_url:
        try:
            return spotify_url.split("track/")[1].split("?")[0]
        except IndexError:
            return None
    return None

def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_names = []
    recommended_artists = []
    recommended_links = []
    for i in distances[1:6]:
        song_name = music.iloc[i[0]].song
        artist_name = music.iloc[i[0]].artist
        spotify_url = get_spotify_track_url(song_name, artist_name)

        recommended_names.append(song_name)
        recommended_artists.append(artist_name)
        recommended_links.append(spotify_url)

    return recommended_names, recommended_artists, recommended_links

st.set_page_config(page_title="Music Recommender", layout="centered")
st.title("🎵 Music Recommender System ")

music_list = music['song'].values
selected_song = st.selectbox("🎧 Select or type a song:", music_list)

if st.button("🔁 Show Recommendation"):
    names, artists, links = recommend(selected_song)

    for i in range(5):
        st.markdown(f"### {names[i]} - {artists[i]}")

        track_id = extract_track_id(links[i])
        if track_id:
            embed_url = f"https://open.spotify.com/embed/track/{track_id}"
            components.iframe(embed_url, width=300, height=80)
         
        else:
            st.warning("⚠️ Spotify track not available.")
