import urllib.parse
import urllib.request
import urllib.error
import json

from helpers import authentication
from helpers import utilities


def get_genres_abridged():
    return [
        "alternative", "ambient", "blues", 
        "chill", "country", "dance", "electronic", "folk", 
        "funk", "happy", "hip-hop", "indie-pop", "jazz", "k-pop", "metal", 
        "new-release", "pop", "punk", "reggae", "rock",
        "soul", "study", "trance", "work-out", "world-music"
    ]


def get_tracks(search_term: str, simplify: bool = True):
    """
    Retrieves a list of Spotify tracks, given the search term passed in.
        * search_term (str): [Required] A search term (for a song), represented as a string.
        * simplify (bool):   Indicates whether you want to simplify the data that is returned.
    Returns a list of tracks.
    """
    search_term = urllib.parse.quote_plus(search_term)
    url = 'https://api.spotify.com/v1/search?q=' + search_term + '&type=track'
    data = _issue_get_request(url)
    if not simplify:
        return data
    return _simplify_tracks(data['tracks']['items'])


def get_top_tracks_by_artist(artist_id: str, simplify: bool = True):
    """
    Retrieves a list of Spotify "top tracks" by an artist
        * artist_id (str): [Required] The Spotify id of the artist.
        * simplify (bool):   Indicates whether you want to simplify the data that is returned.
    Returns a list of tracks.
    """
    url = 'https://api.spotify.com/v1/artists/' + artist_id + '/top-tracks?country=us'
    # print(url)
    data = _issue_get_request(url)
    if not simplify:
        return data
    return _simplify_tracks(data['tracks'])


def get_artists(search_term: str, simplify: bool = True):
    """
    Retrieves a list of Spotify artists, given the search term passed in.
        * search_term (str): [Required] A search term (for an artist), represented as a string.
        * simplify (bool):   Indicates whether you want to simplify the data that is returned.
    Returns a list of artists.
    """
    search_term = urllib.parse.quote_plus(search_term)
    url = 'https://api.spotify.com/v1/search?q=' + search_term + '&type=artist'
    data = _issue_get_request(url)
    if not simplify:
        return data
    return _simplify_artists(data['artists']['items'])


def get_similar_tracks(artist_ids: list, track_ids: list, genres: list, simplify: bool = True):
    """
    Spotify's way of providing recommendations. One or more params is required: 
    artist_ids, track_ids, or genres. Up to 5 seed values may be provided in 
    any combination of seed_artists, seed_tracks and seed_genres. In other words:
    len(artist_ids) + len(track_ids) + len(genres) between 1 and 5.
        * artist_ids (list): A list of artist ids
        * track_ids (list): A list of track ids
        * genres (genres): A list of genres
    Returns a list of tracks that are similar
    """
    if not artist_ids and not track_ids and not genres:
        raise Exception('Either artist_ids, track_ids, or genres  are required')
    
    # check if seeds <= 5:
    artist_ids = artist_ids or []
    track_ids = track_ids or []
    genres = genres or []
    if len(artist_ids) + len(track_ids) + len(genres) > 5:
        error = 'You can only have 5 "seed values" in your recommendations query.\n' + \
            'In other words, (len(artist_ids) + len(track_ids) + len(genres)) must be less than or equal to 5.'
        raise Exception(error)
    
    params = []
    if artist_ids:
        params.append('seed_artists=' + ','.join(artist_ids))
    if track_ids:
        params.append('seed_tracks=' + ','.join(track_ids))
    if genres:
        params.append('seed_genres=' + ','.join(genres))
    
    url = 'https://api.spotify.com/v1/recommendations?' + '&'.join(params)
    print(url)
    data = _issue_get_request(url)
    if not simplify:
        return data

    return _simplify_tracks(data['tracks'])


############################################
# Some private, helper functions utilities #
############################################
# retrieves data from any Spotify endpoint:
def _issue_get_request(url):
    token = authentication.get_token('https://www.apitutor.org/spotify/key')
    request = urllib.request.Request(url, None, {
        'Authorization': 'Bearer ' + token
    })
    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        # give a good error message:
        error = utilities.get_error_message(e, url)
    raise Exception(error)


def _simplify_tracks(tracks: list):
    try:
        tracks[0]
    except Exception:
        return tracks

    simplified = []
    # print(tracks[0])
    for item in tracks:
        track = { 
            'id': item['id'], 
            'name': item['name'], 
            'preview_url': item['preview_url'],
            'share_url': 'https://open.spotify.com/track/' + item['id']
        }
        try:
            track['album'] = {
                'id': item['album']['id'],
                'name': item['album']['name'],
                'image_url': item['album']['images'][0]['url'],
                'image_url_small': item['album']['images'][-1]['url'],
                'share_url': 'https://open.spotify.com/album/' + item['album']['id']
            }
        except Exception:
            pass
        try:
            artists = item.get('album').get('artists')
            artist = artists[0]
            track['artist'] = { 
                'id': artist['id'], 
                'name': artist['name'],
                'share_url': 'https://open.spotify.com/artist/' + item['album']['artists'][0]['id']
            }
        except Exception:
            pass
        simplified.append(track)
    return simplified


def _simplify_artists(artists: list):
    try:
        artists[0]
    except Exception:
        return artists

    simplified = []
    for item in artists:
        artist = { 
            'id': item['id'], 
            'name': item['name'], 
            'genres': ', '.join(item['genres']),
            'share_url': 'https://open.spotify.com/artist/' + item['id']
        }
        try:
            artist['image_url'] = item['images'][0]['url']
            artist['image_url_small'] = item['images'][-1]['url']
        except Exception:
            pass
        simplified.append(artist)
    return simplified
