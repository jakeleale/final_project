import os
from flask import Flask, render_template, session, request, url_for, redirect, flash
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.secret_key = os.urandom(24)

#App Credentials
cid = '6a8142a18677431488beba396753df53'
secret = '8836f10ee23f451986ef72955854ef08'
redirect_uri = 'https://jakeleale.pythonanywhere.com/callback'
scope = "user-library-read user-top-read user-read-private playlist-modify-public playlist-modify-private"

def get_spotify_oauth():
    cache_handler = FlaskSessionCacheHandler(session)
    return SpotifyOAuth(
        client_id=cid,
        client_secret=secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_handler=cache_handler,
        show_dialog=True
    )

#Home Page
@app.route("/")
def home():
    return render_template("main_doc.html")

#Login Start
@app.route("/start")
def start():
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_cached_token()

    if not sp_oauth.validate_token(token_info):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    session["token_info"] = token_info
    return redirect(url_for('home'))

def get_token():
    sp_oauth = get_spotify_oauth()
    token_info = session.get("token_info")

    if not token_info:
        print("No token in session.")
        return None

    if sp_oauth.is_token_expired(token_info):
        print("Token expired, refreshing...")
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session["token_info"] = token_info
            print("Refreshed token:", token_info)
        except Exception as e:
            print("Failed to refresh token:", e)
            return None

    return token_info


#Call back - approved on Spotify developer dashboard
@app.route('/callback')
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get('code')
    error = request.args.get('error')

    if error or not code:
        flash("You must approve Spotify access to use the app.")
        return redirect(url_for('home'))

    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('get_liked_songs'))



# Displaying Saved Library
@app.route('/get_liked_songs', methods=['GET', 'POST'])
def get_liked_songs():
    sp_oauth = get_spotify_oauth()
    token_info = session.get("token_info")

    if not token_info or not sp_oauth.validate_token(token_info):
        return redirect(url_for("start"))

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session["token_info"] = token_info

    sp = Spotify(auth=token_info["access_token"])
    print(sp.me())
    sort_method = request.args.get("sort", "default")

    try:
        results = sp.current_user_saved_tracks(limit=50)
    except Exception as e:
        return f"Error retrieving saved tracks: {str(e)}"

    tracks = []
    track_ids = []

    def format_duration(ms):
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"


    for item in results["items"]:
        track = item["track"]
        if track and track.get("id"):
            tracks.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "url": f"https://open.spotify.com/track/{track['id']}",
                "popularity": track["popularity"],
                "release_date": track["album"]["release_date"],
                "duration_ms": format_duration(track['duration_ms']),
                "id": track["id"]
            })
            track_ids.append(track["id"])

     # Handle POST request for saving selected tracks
    if request.method == 'POST':
        selected_tracks = request.form.getlist('selected_tracks')  # List of selected track IDs
        session['cart'] = selected_tracks  # Store selected tracks in session


    #sorting
    if sort_method == "popularity":
        tracks.sort(key=lambda x: x["popularity"], reverse=True)
    elif sort_method == "duration_ms":
        tracks.sort(key=lambda x: x["duration_ms"], reverse=True)
    elif sort_method == "release_date":
        tracks.sort(key=lambda x: x["release_date"], reverse=True)

    return render_template("liked_songs.html", tracks=tracks, sort=sort_method)

@app.route('/top_songs', methods=['GET', 'POST'])
def top_songs():
    sp_oauth = get_spotify_oauth()
    token_info = session.get("token_info")

    if not token_info or not sp_oauth.validate_token(token_info):
        return redirect(url_for("start"))

    sp = Spotify(auth_manager=sp_oauth)
    time_range = request.args.get("time_range", "medium_term")

    try:
        results = sp.current_user_top_tracks(limit=10, time_range=time_range)
    except Exception as e:
        return f"Error fetching top tracks: {str(e)}"

    top_tracks = []
    for item in results["items"]:
        track = {
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "url": f"https://open.spotify.com/track/{item['id']}",
            "popularity": item["popularity"],
            "release_date": item["album"]["release_date"]
        }
        top_tracks.append(track)

        if request.method == 'POST':
            selected_tracks = request.form.getlist('selected_tracks')  # List of selected track IDs
            session['cart'] = selected_tracks  # Store selected tracks in session

    return render_template("top_songs.html", tracks=top_tracks, time_range=time_range)

@app.route('/top_artists', methods=['GET', 'POST'])
def top_artists():
    sp_oauth = get_spotify_oauth()
    token_info = session.get("token_info")

    if not token_info or not sp_oauth.validate_token(token_info):
        return redirect(url_for("start"))

    sp = Spotify(auth_manager=sp_oauth)
    time_range = request.args.get("range", "medium_term")

    try:
        results = sp.current_user_top_artists(limit=10, time_range=time_range)
        top_artists = []

        for artist in results["items"]:
            top_tracks_result = sp.artist_top_tracks(artist["id"], country="US")
            top_tracks = []

            for track in top_tracks_result["tracks"][:5]:
                top_tracks.append({
                    "name": track["name"],
                    "preview_url": track["preview_url"],
                    "url": track["external_urls"]["spotify"]
                })

            top_artists.append({
                "name": artist["name"],
                "genres": ", ".join(artist["genres"]) if artist["genres"] else "N/A",
                "image_url": artist["images"][0]["url"] if artist["images"] else None,
                "url": artist["external_urls"]["spotify"],
                "popularity": artist["popularity"],
                "top_tracks": top_tracks
            })

            if request.method == 'POST':
                selected_tracks = request.form.getlist('selected_tracks')  # List of selected track IDs
                session['cart'] = selected_tracks  # Store selected tracks in session

    except Exception as e:
        return f"Error fetching top artists: {str(e)}"

    return render_template("top_artists.html", artists=top_artists, time_range=time_range)

@app.route('/update_cart', methods=["POST"])
def update_cart():
    selected_tracks = request.form.getlist("selected_tracks")
    redirect_back = request.form.get("redirect_back", url_for("playlist"))

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    for track_id in selected_tracks:
        if track_id not in cart:
            cart.append(track_id)
    session["cart"] = cart

    return redirect(redirect_back)


@app.route("/playlist")
def playlist():
    token_info = get_token()
    if not token_info:
        return redirect(url_for("start"))

    sp = Spotify(auth=token_info["access_token"])
    track_ids = session.get("cart", [])

    if not track_ids:
        return render_template("playlist.html", tracks=[])

    try:
        results = sp.tracks(track_ids)
        tracks = [{
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "url": track["external_urls"]["spotify"],
            "id": track["id"]
        } for track in results["tracks"]]
    except Exception as e:
        return f"Error loading playlist: {str(e)}"

    return render_template("playlist.html", tracks=tracks)

@app.route("/export_playlist", methods=["POST"])
def export_playlist():
    token_info = get_token()
    if not token_info:
        return redirect(url_for("start"))

    sp = Spotify(auth=token_info["access_token"])
    user_id = sp.me()["id"]

    cart = session.get("cart", [])
    if not cart:
        return "No songs in cart to export.", 400

    playlist_name = request.form.get("playlist_name", "My Exported Playlist")
    try:
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
        sp.playlist_add_items(playlist_id=playlist["id"], items=cart)
    except Exception as e:
        return f"Failed to export playlist: {str(e)}"

    return redirect(playlist["external_urls"]["spotify"])


#Logout of Spotify and clear the session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Running the App
if __name__ == "__main__":
    app.run(debug=False)




