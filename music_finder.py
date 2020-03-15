import pandas as pd

from helpers import spotify
from helpers import utilities
from helpers import sendgrid


# Initialize the options menu
menu = pd.DataFrame(
    data={
        'Selection Number': list(range(1, 6)),
        'User Option': ['Select your favorite genres ',
                        'Select your favorite artists',
                        'Select your favorite tracks ',
                        'Discover new music          ',
                        'Quit                        '],
        'User Input': [''] * 5
    }
).set_index('Selection Number')


def print_menu(data: pd.DataFrame):
    """
    Prints the options menu with left-justified columns

    :param data: options menu data frame
    :return: None
    """
    with pd.option_context('display.colheader_justify', 'left'):
        print(data, '\n')


def get_genre(data: pd.DataFrame, genre_list: list):
    """
    Allows user to select new genres and displays list of genres for selection

    :param data: options menu data frame
    :param genre_list: list of selected genres
    :return: updated options menu data frame and selected genres list
    """

    # Retrieve abridged genres list
    genres = spotify.get_genres_abridged()

    # Create data frame for genres with 'X' on selected genre(s)
    genre_dict = pd.DataFrame(
        data={
            'Selection Number': list(range(1, len(genres)+1)),
            'Genre': genres,
            'Selected': ['X' if n in genre_list else '' for n in genres]
        }
    ).set_index('Selection Number')

    print_menu(genre_dict)

    # Allow user to select new genres
    # Split selection on commas and strip extraneous spaces
    ans = input('\nPlease enter a comma-delimited list of numbers, or type "clear" to clear selected genres. ')
    selection = [n.strip() for n in ans.split(',')]

    # If 'clear' is given, reset the options menu dataframe and genres list
    if 'clear' in selection:
        data.loc[1]['User Input'] = ''
        genre_list = list()
        print('Genres cleared!\n')

    else:
        # Try to convert selection to integers and select corresponding dictionary entries
        try:
            selection = list(map(int, selection))
            selection = [genres[n - 1] for n in selection]

        # Return to the menu if any one of these operations fails
        except (ValueError, IndexError):
            print('Invalid selection!', 'Going back to menu...', '', sep='\n')
            return data, genre_list

        # Update the selected genres list by taking only unique values
        genre_list = list(set(genre_list + selection))

        # Update the options menu by casting the updated list as a comma-separated string
        data.loc[1]['User Input'] = ', '.join(genre_list)

    return data, genre_list


def get_artist_list(search_term: str, display: int = 10):
    """
    Allows the user to search for artists on spotify, then prints and returns the result

    :param search_term: user input used to query spotify
    :param display: number of artists to display in results (default 10)
    :return: data frame of artist information and their corresponding IDs
    """

    # Retrieve results from spotify given artist query
    search_result = spotify.get_artists(search_term)

    # Construct data frame of artist names and their genres with query result
    artist_data = pd.DataFrame(
        data=search_result,
        index=list(range(1, len(search_result) + 1)),
        columns=['name', 'genres']
    ).rename(columns={'name': 'Artist', 'genres': 'Genre'})
    artist_data.index.rename('Selection Number', inplace=True)

    # Create a list of artist IDs from the query result
    artist_ids = [item['id'] for item in search_result]

    # If the artist query is not empty, print the data and return the data and ID list
    if not artist_data.empty:
        print('\nWe found the following artists...\n')
        print_menu(artist_data.head(display))
        return artist_data, artist_ids

    # Otherwise, return None
    else:
        print('\nNo artists found!')
        return None, None


def get_track_list(search_term: str, criterion: str, display: int = 10):
    """
    Allows the user to search for tracks by artist or title, then prints and returns the result

    :param search_term: user input used to query spotify
    :param criterion: determines whether to query by artist or track title
    :param display: number of tracks to display in results (default 10)
    :return: data frame of track information and their corresponding IDs
    """

    # Query spotify by artist if such criterion is given, otherwise by track title
    if criterion == 'artist':
        search_result = spotify.get_top_tracks_by_artist(search_term)
    else:
        search_result = spotify.get_tracks(search_term)

    # Construct a data frame of track titles and their albums with query result
    track_data = pd.DataFrame(
        data={
            'Selection Number': list(range(1, len(search_result) + 1)),
            'Song Title': [item['name'] for item in search_result],
            'Album': [item['album']['name'] for item in search_result]
        }
    ).set_index('Selection Number')

    # Create a list of track IDs from the query result
    track_ids = [item['id'] for item in search_result]

    # If the track query is not empty, print the data and return the data and ID list
    if not track_data.empty:
        print('\nWe found the following tracks...\n')
        print_menu(track_data.head(display))
        return track_data, track_ids

    # Otherwise, return None
    else:
        print('\nNo tracks found!')
        return None, None


def get_artist(data: pd.DataFrame, artists: list):
    """
    Allows the user to select new artists and updates the list of selected artists

    :param data: options menu data frame
    :param artists: list of selected artist IDs
    :return: updated options menu data frame and selected artist list
    """

    # Query the user for an artist and retrieve the results
    search_term = input('\nEnter the name of an artist: ')
    artist_data, artist_ids = get_artist_list(search_term)

    # If the search yields no results, return the arguments without updating them
    if artist_data is None:
        print('Going back to menu...\n')
        return data, artists

    # Allow the user to select new artists
    # Split the selection by commas and strip extraneous spaces
    ans = input('Select artist by entering a comma-delimited list of numbers,'
                'or type "clear" to clear artist selections. ')
    selection = [n.strip() for n in ans.split(',')]

    # If 'clear' is given, reset the options menu cell and selected artists list
    if 'clear' in selection:
        data.loc[2]['User Input'] = ''
        artists = list()
        print('Artists cleared!\n')
    else:
        # Try to cast selection to integers and select corresponding artists and their IDs
        try:
            selection = [int(n) for n in selection]
            ids = [artist_ids[n - 1] for n in selection]
            selection = artist_data.loc[selection]['Artist'].to_list()

        # Return to the menu if any of these operations fail
        except (ValueError, KeyError, IndexError):
            print('Invalid selection!', 'Going back to menu...', '', sep='\n')
            return data, artists

        # Update the list of selected artists with unique entries
        artists = list(set(artists + ids))

        # Obtain selected artist names from the menu
        selected_artists = [n.strip() for n in data.loc[2]['User Input'].split(',')]

        # If the artist menu cell is empty, update it with only new selections
        if selected_artists == ['']:
            data.loc[2]['User Input'] = ', '.join(selection)

        # Otherwise, update it with the union of new and selected artist names
        else:
            selected_artists = set(selected_artists + selection)
            data.loc[2]['User Input'] = ', '.join(selected_artists)

    return data, artists


def get_artist_tracks(criterion: str):
    """
    Allows the user to search for top tracks by a given artist

    :param criterion: determines whether to retrieve tracks by artist or title
    :return: data frame of matching tracks and list of their IDs
    """

    # Allow the user to search for an artist and retrieve the result
    search_term = input('\nEnter the name of an artist: ')
    artist_data, artist_ids = get_artist_list(search_term)

    # Return None if the search does not yield any resutls
    if artist_data is None:
        return None, None

    # Try to cast selection as integer and select corresponding artist ID
    try:
        selection = int(input('Select ONE artist to see their top tracks: ').strip())
        artist_id = artist_ids[selection - 1]

    # Return None if any of these operations fail
    except (ValueError, IndexError):
        print('\nInvalid selection!')
        return None, None

    # Retrieve track data and IDs by querying with the artist IF
    track_data, track_ids = get_track_list(artist_id, criterion=criterion)

    # Return None if the search yields no results, otherwise return the track data and their IDs
    if track_data is None:
        return None, None
    else:
        return track_data, track_ids


def get_tracks(data: pd.DataFrame, tracks: list):
    """
    Allows the user to select new tracks and updates the list of selected tracks

    :param data: options menu data frame
    :param tracks: list of selected track IDs
    :return: updated options menu data frame and list of track IDs
    """

    # Ask the user to search for tracks by artist or title
    # Strip extraneous spaces and cast the response to lowercase
    ans = input('Would you like to search by artist or title? ').strip().lower()

    # Return to menu if the response is not one of 'artist' or 'title'
    if ans not in ['artist', 'title']:
        print('Invalid selection!', 'Going back to menu...', '', sep='\n')
        return data, tracks
    else:
        # Retrieve track data by artist if the user opts to do so
        if ans == 'artist':
            track_data, track_ids = get_artist_tracks(ans)

        # Otherwise, retrieve data by querying spotify with a track title
        else:
            search_term = input('\nEnter the name of a track: ')
            track_data, track_ids = get_track_list(search_term, criterion=ans)

    # Return to menu is the resulting track data is None
    if track_data is None:
        print('Going back to menu...\n')
        return data, tracks

    # Allow the user to select one of the given tracks
    ans = input('Select tracks by entering a comma-delimited list of numbers,'
                'or type "clear" to clear track selections. ')
    selection = [n.strip() for n in ans.split(',')]

    # If 'clear' is given, reset the options menu and list of selected track IDs
    if 'clear' in selection:
        data.loc[3]['User Input'] = ''
        tracks = list()
        print('Tracks cleared!\n')
    else:
        # Try to cast the selection to integers, then select corresponding tracks and their IDs
        try:
            selection = list(map(int, selection))
            ids = [track_ids[n - 1] for n in selection]
            selection = track_data.loc[selection]['Song Title'].to_list()

        # If any of these operations fail, return to the menu
        except (ValueError, KeyError, IndexError):
            print('Invalid Selection!', 'Going back to menu...', '', sep='\n')
            return data, tracks

        # Update the track ID list with unique values
        tracks = list(set(tracks + ids))

        # Obtain the names of previously selected tracks from the menu
        selected_tracks = [n.strip() for n in data.loc[3]['User Input'].split(',')]

        # If the selected tracks cell is empty, update it with only new selections
        if selected_tracks == ['']:
            data.loc[3]['User Input'] = ', '.join(selection)

        # Otherwise, update the cell with the unique titles of new and selected tracks
        else:
            selected_tracks = set(selected_tracks + selection)
            data.loc[3]['User Input'] = ', '.join(selected_tracks)

    return data, tracks


def get_similar_tracks(data: pd.DataFrame, artist_ids: list, track_ids: list, genres: list, max_size: int = 5):
    """
    Queries spotify to obtain similar tracks given the selected genres, artists and tracks,
    then writes these recommendations to a file or emails it to/from the user

    :param data: options menu data frame
    :param artist_ids: list of selected artist IDs
    :param track_ids: list of selected track IDs
    :param genres: list of selected genres
    :param max_size: maximum number of seed parameters
    :return: None
    """

    # Initialize list of maximum seeds
    n, positions = 0, [max_size] * 3

    # Reduce number of viable positions by lengths of seed parameters provided
    # This ensures that only five of the given parameters are chosen
    for i, lst in enumerate([artist_ids, track_ids, genres]):
        if n > max_size:
            positions[i] = 0
        else:
            positions[i] -= n
            n += len(lst)

    # Retrieve similar tracks from seed parameters given
    track_data = spotify.get_similar_tracks(
        artist_ids[:positions[0]],
        track_ids[:positions[1]],
        genres[:positions[2]]
    )

    # Cast data to a flattened data frame
    track_table = utilities.get_dataframe(track_data)

    # Select track title, artist, and album from data frame and rename these columns
    keys = ['name', 'artist_name', 'album_name']
    new_keys = ['Song Title', 'Artist', 'Album Name']
    display_table = track_table[keys].rename(columns=dict(zip(keys, new_keys)))
    display_table.index.rename('', inplace=True)
    print_menu(display_table)

    # Gather HTML content and file name, then prompt the user to write the output to file
    ans = input('Would you like to write these recommendations to a file?[y/n] ')
    file_name = utilities.name_file()

    # Append the HTML data frame to a header constructed from seed parameters
    html_content = utilities.get_html_header(data) + '\n' + \
        utilities.get_formatted_tracklist_table_html(track_table)

    if ans.lower() == 'yes' or ans.lower() == 'y':
        with open(file_name, mode='w') as f:
            f.write(html_content)
            f.close()
            print('Written to file: %s\n' % file_name[2:])

    # Send the HTML content by email and attach HTML file if one was created
    sendgrid.email(html_content, file_name)


def music_finder(data: pd.DataFrame):
    """
    Handles user queries and runs music selection program

    :param data: an empty user options data frame
    :return: None
    """

    # Initialize empty lists of genres, artist IDs and track IDs
    genres = list()
    artists = list()
    tracks = list()

    # Construct infinite loop
    while True:

        # First, print options menu to screen and check the number of its parameters
        print_menu(data)
        utilities.check_length(genres, artists, tracks)

        # Query the user to select an option and ask again if the selection is invalid
        query = input('What would you like to do? ')
        while query not in list(map(str, data.index.values)):
            print('Invalid Choice!\n')
            query = input('What would you like to do?')

        # Allow the user to select genres, artists, and tracks given their selection
        # Update the options menu and corresponding list after doing so
        if int(query) == 1:
            data, genres = get_genre(data, genres)

        elif int(query) == 2:
            data, artists = get_artist(data, artists)

        elif int(query) == 3:
            data, tracks = get_tracks(data, tracks)

        elif int(query) == 4:
            get_similar_tracks(
                data=data,
                artist_ids=artists,
                track_ids=tracks,
                genres=genres
            )

        elif int(query) == 5:
            print('\nQuitting...')
            exit(0)


if __name__ == '__main__':
    music_finder(menu)
