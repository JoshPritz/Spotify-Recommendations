import os
import time
import traceback
import collections
import pandas as pd


#######################
# Data Frame Handling #
#######################

def flatten(d: dict, parent_key: str = '', sep: str = '_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def flatten_for_pandas(data: list):
    """
    Converts a list of nested dictionaries into a list of flattened 
    dictionaries that can be more easilty displayed using pandas.
        * data (list): [Required] a list of dictionaries
    Returns a flattened list of dictionaries (list).
    """
    flattened_list = []
    count = 1
    for item in data:
        item = flatten(item)
        item['num'] = count
        flattened_list.append(item)
        count += 1
    return flattened_list


def get_dataframe(data: list):
    """
    Converts a list of dictionaries into a flattened pandas dataframe.
    """
    flattened_list = flatten_for_pandas(data)
    return pd.DataFrame(flattened_list).set_index('num')


##################################
# HTML Generation and Formatting #
##################################

def get_formatted_tracklist_table_html(track_data: pd.DataFrame):
    """
    Makes a nice formatted HTML table of tracks. Good for writing to an
    HTML file or for sending in an email.
        * tracks(list): [Required] A list of tracks
    Returns an HTML table as a string
    """
    if track_data.empty:
        print('A list of tracks is required.')
        return
    pd.set_option('display.max_colwidth', None)
    keys = ['name', 'album_image_url_small', 'artist_name', 'album_name', 'share_url']
    new_keys = ['Song Title', 'Cover Art', 'Artist', 'Album', 'Share URL']
    track_data = track_data[keys].rename(columns=dict(zip(keys, new_keys)))

    def image_formatter(im):
        return f'<img src="{im}" />'

    formatters = {
        'Cover Art': image_formatter
    }
    playlist_table = track_data.to_html(formatters=formatters, escape=False, index=False, render_links=True)
    playlist_table = playlist_table.replace('style="text-align: right;"', '')
    playlist_table = playlist_table.replace('<tr>', '<tr style="border: solid 1px #CCC;">')
    playlist_table = playlist_table.replace(
        '<table border="1" class="dataframe">',
        '<table style="border-collapse: collapse; border: solid 1px #CCC;">'
    )
    return playlist_table


def get_html_header(data: pd.DataFrame):

    genres = data['User Input'][1]
    artists = data['User Input'][2]
    tracks = data['User Input'][3]

    header = """
    <style type="text/css">
      .tab {{ margin-left: 40px; }}
      body {{ font-family: Sans-Serif }}
      table {{ font-family: Sans-Serif }}
    </style>
    <body>
      <h1>
        We found the following songs you might like!
      </h1>
      <h3>
        Thank you for telling us you like:
      </h3>
      <h3 class="tab">
        Artists: {artists} <br>
        Tracks: {tracks} <br>
        Genres: {genres} <br>
      </h3>
    </body>
    """

    return header.format(artists=artists, tracks=tracks, genres=genres)


################
# Main Helpers #
################

def name_file():
    """
    Returns a unique file name for the HTML ouput

    :return: HTML file name
    """

    # Obtain today's date and append the date to the file name
    save_date = time.strftime('%y%h%d', time.gmtime(time.time()))
    file_name = './Recommendations_%s.html' % save_date

    # If the first name taken, append an incrementing number until the file name is not taken
    n = 0
    while os.path.isfile(file_name):
        n += 1
        file_name = file_name[:25] + '_%d.html' % n

    return file_name


def check_length(list_1, list_2, list_3):
    """
    Prints a warning if the user accrues more than five parameters

    :param list_1: list of selected genres
    :param list_2: list of selected artists
    :param list_3: list of selected tracks
    :return: None
    """

    if len(list_1) + len(list_2) + len(list_3) > 5:
        print('\nWarning!', 'Only five genres/artists/songs may be used for recommendation.',
              'Entering more inputs will not change the result...\n', sep='\n')


##################
# Error Handling #
##################

def get_error_message(e, url=None):
    errors = []
    if url:
        errors.append('This URL is invalid: ' + url)
    tokens = traceback.format_exc().split('\n')
    if len(tokens):
        errors.extend(tokens[0:3])
    return '\n'.join(errors)
