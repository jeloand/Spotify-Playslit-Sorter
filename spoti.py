import spotipy
from spotipy.oauth2 import SpotifyOAuth

from keys import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

scope = "playlist-read-private playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri="http://localhost:8080"))

def reduce_tracks_info(tracks):
    reduced_tracks_info = []
    for track in tracks["items"]:
        track_info = {}
        track_info["name"] = track["track"]["name"]
        track_info["uri"] = track["track"]["uri"]
        track_info["cover"] = track["track"]["album"]["images"][2]["url"]
        reduced_tracks_info += [track_info]
    return reduced_tracks_info

def get_dominant_color(image_url):
    # from io import BytesIO
    #
    # import requests
    # from PIL import Image
    #
    # resp = requests.get(image_url)
    # assert resp.ok
    # img = Image.open(BytesIO(resp.content))
    #
    # img2 = img.resize((1, 1))
    #
    # color = img2.getpixel((0, 0))
    # return color

    # from colorthief import ColorThief
    # return ColorThief(image_url).get_color(quality=1)

    from PIL import Image
    import requests

    img = Image.open(requests.get(image_url, stream=True).raw)

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=8)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]

    return dominant_color

def sort_tracks(tracks):
    import colorsys

    # tracks.sort(key=lambda track: colorsys.rgb_to_hls(*track["color"]))

    tracks.sort(key=lambda track: track["color"])

    return tracks

# def main():
playlists = sp.current_user_playlists()
for index, item in enumerate(playlists["items"]):
    print(f"{str(index).rjust(2)} - {item['name']}")

index = int(input("Enter playlist you want to sort: "))
playlist_id = playlists["items"][index]["id"]

playlist_id

tracks = sp.playlist_tracks(playlist_id)
tracks_info = reduce_tracks_info(tracks)

tracks_info


tracks_info[0]["color"] = get_dominant_color(tracks_info[0]["cover"])

for track in tracks_info:
    track["color"] = get_dominant_color(track["cover"])

tracks_sorted = sort_tracks(tracks_info)

new_playlist = sp.user_playlist_create(sp.me()["id"], "test")
tracks_uri = [track["uri"] for track in tracks_sorted]
sp.playlist_add_items(new_playlist["id"], tracks_uri)



#
# if __name__ == "__main__":
#     main()
