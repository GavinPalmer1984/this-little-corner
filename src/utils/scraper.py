from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtubesearchpython import Playlist
from elasticsearch import Elasticsearch
import json
import requests
import os
import re
import isodate

insecure_prod_hashtag_yolo = 'http://this-little-corner.com:80/indexer' # todo security i guess
index_name = os.getenv('INDEX_NAME', 'this_little_corner')

domain = os.getenv('ES_HOST')
port = os.getenv('ES_PORT')
username = os.getenv('ES_USERNAME')
password = os.getenv('ES_PASSWORD')
cert = os.getenv('ES_TLS_CRT')
yt_api_key = os.getenv('YOUTUBE_API_KEY')
get_yt_channels_from_tlc_api = os.getenv('GET_YOUTUBE_CHANNELS_FROM_TLC_API', True)
get_yt_channels_from_env = os.getenv('GET_YOUTUBE_CHANNELS_FROM_ENV', False)
yt_channels_from_env = os.getenv('YOUTUBE_CHANNELS_FROM_ENV')

if not domain and not port:
    domain = 'this-little-corner-elastic.ngrok.io'
    port = 80


def get_channels():
    if get_yt_channels_from_tlc_api != '0':
        channels = requests.get('http://this-little-corner.com/api/channels').content
        # [{"Id":"UCCebR16tXbv5Ykk9_WtCCug","Name":"Agapologia","SearchNames":["agapologia","golden"]}]
    elif get_yt_channels_from_env == '1':
        channels = yt_channels_from_env
    return json.loads(channels)


def get_video_details(key, video_id):

    headers = {
        'Accept': 'application/json',
    }

    params = (
        ('part', 'snippet,contentDetails'),
        ('id', video_id),
        ('key', key),
    )

    response = requests.get('https://youtube.googleapis.com/youtube/v3/videos', headers=headers, params=params)
    content = json.loads(response.content)
    if 'items' not in content:
        print('invalid response: will not index')
    return content['items'][0]['snippet'], content['items'][0]['contentDetails']


def create_index(es_object):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "video_id": {"type": "text"},
                "channel_id": {"type": "text"},
                "channel_name": {"type": "text"},
                "title": {"type": "text"},
                "url": {"type": "text"},
                "date": {"type": "date"},
                "description": {"type": "text"},
                "duration": {"type": "integer"},
                "transcript_full": {"type": "text"},
                "transcript_parts": {
                    "properties": {
                        "text": {"type": "text"},
                        "start": {"type": "float"},
                        "duration": {"type": "float"}
                    }
                },
            }
        }
    }

    try:
        if not es_object.indices.exists(index=index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            result = es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index: ' + json.dumps(result))
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def store_record(elastic_object, video_id, record):
    is_stored = True
    try:
        outcome = elastic_object.index(index=index_name, id=video_id, document=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
        is_stored = False
    finally:
        return is_stored


def already_exists(elastic_object, video_id):
    resp = elastic_object.search(index=index_name, query={
            'match': {
                'video_id': video_id,
            }
    })
    if resp['hits']['total']['value'] > 0:
        return resp['hits']['hits'][0]['_source']['transcript_full'] != ''
    return False


def connect_elasticsearch():
    print(domain, port, cert, username, password)
    if domain and port and cert and username and password:
        _es = Elasticsearch([{'host': domain, 'port': int(port), 'scheme': 'https'}], ca_certs=cert, request_timeout=5, basic_auth=(username, password))
    elif domain and port and username and password:
        _es = Elasticsearch([{'host': domain, 'port': int(port), 'scheme': 'http'}], request_timeout=5, basic_auth=(username, password))
    else:
        _es = Elasticsearch([insecure_prod_hashtag_yolo], timeout=5)
    if _es.ping():
        print('elasticsearch is connected')
        return _es
    else:
        print('could not connect to elasticsearch')
        return None


def get_transcript(video_id, channel_id = None):
    transcript_array = []
    if channel_id:
        transcript_file = os.path.join("src", "data", "raw_transcripts", channel_id, f"{video_id}.txt")
        if os.path.exists(transcript_file):
            with open(transcript_file, 'r', encoding='utf-8') as file:
                transcript = file.read()
            print(f"Transcript found for video {video_id} in the local file system.")

            for line in transcript.split('\n'):
                match = re.match(r'(\d+\.\d+)\s*-\s*(\d+\.\d+):\s*(.*)', line)
                if match:
                    start, duration, text = match.groups()
                    transformed_line = {
                        'text': text.strip(),
                        'start': float(start),
                        'duration': float(duration)
                    }
                    transcript_array.append(transformed_line)
            return transcript_array
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return []


def convert_to_seconds(time_string):
    parts = time_string.split(':')
    parts.reverse()
    seconds = 0
    multiplier = 1
    for part in parts:
        seconds += int(part) * multiplier
        multiplier *= 60
    return seconds

def store_video(elastic, youtube_api_key, channel_id, channel_name, video_id, video_title, video_url, video_seconds):

    if already_exists(es, video_id):
        print(f'Already indexed video {video_id} ({video_title})')
        return

    try:
        more_details, content_details = get_video_details(youtube_api_key, video_id)
        video_description = more_details['description']
        video_date = more_details['publishedAt'].split('T')[0]
        transcript_parts = get_transcript(video_id, channel_id)
        transcript_full_string = ' '.join([x['text'] for x in transcript_parts])

        to_index = {
            'video_id': video_id,
            'channel_id': channel_id,
            'channel_name': channel_name,
            'title': video_title,
            'url': video_url,
            'date': video_date,
            'description': video_description,
            'duration': video_seconds,
            'transcript_full': transcript_full_string,
            'transcript_parts': transcript_parts
        }
        to_index_json = json.dumps(to_index)

        store_record(elastic, video_id, to_index_json)
        print(f'Indexed video ({video_title})')
    except Exception as e:
        print(f'Error indexing video ({video_title}): ')

def get_video_ids_from_raw_transcripts(channel_id):
    video_ids = []
    # Define the path to the folder containing transcript files
    data_folder = os.path.join("src", "data", "raw_transcripts", channel_id)
    
    # Create the folder if it doesn't exist
    os.makedirs(data_folder, exist_ok=True)
    
    # Loop through the files in the directory
    for filename in os.listdir(data_folder):
        # Check if the file has a .txt extension
        if filename.endswith(".txt"):
            # Assuming the filename without the extension is the video ID
            video_id = os.path.splitext(filename)[0]
            video_ids.append(video_id)
    
    return video_ids

def index_channel(elastic, name, channel_id):
    print('Indexing ' + name)

    if yt_api_key is None:
        text_file = open("secrets.txt", "r")
        youtube_api_key = text_file.read()
        text_file.close()
    else:
        youtube_api_key = yt_api_key

    from_raw_video_ids = get_video_ids_from_raw_transcripts(channel_id)

    # get all the videos for the channel
    playlist = Playlist(f'https://www.youtube.com/playlist?list=UU{channel_id[2:]}')
    playlist_videos = []
    while playlist.hasMoreVideos:
        print(f'Videos Retrieved: {len(playlist.videos)}')
        playlist_videos += playlist.videos
        playlist.getNextVideos()

    play_list_video_count = len(playlist_videos)
    from_raw_video_count = len(from_raw_video_ids)
    print(f'Found {play_list_video_count} playlist videos and {from_raw_video_count} raw transcripts.')
    channel_name = None

    i = 1
    for video in playlist_videos:
        video_id = video['id']
        print(f'Processing playlist video {i} of {play_list_video_count} id {video_id}')
        i = i + 1
        if video['id'] in from_raw_video_ids:
            from_raw_video_ids.remove(video['id'])

        channel_name = video['channel']['name']
        video_title = video['title']
        video_url = video['link'].split('&')[0]
        if video['duration'] is None:
            continue
        video_seconds = convert_to_seconds(video['duration'])
        store_video(elastic, youtube_api_key, channel_id, channel_name, video_id, video_title, video_url, video_seconds)

    from_raw_video_count = len(from_raw_video_ids)
    i = 1
    for video_id in from_raw_video_ids:
        print(f'Processing playlist video {i} of {from_raw_video_count} id {video_id}')
        i = i + 1
        more_details, content_details = get_video_details(youtube_api_key, video_id)
        channel_name = more_details['channelTitle']
        video_title = more_details['title']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_duration_iso = content_details['duration']
        video_seconds = isodate.parse_duration(video_duration_iso).total_seconds()
        store_video(elastic, youtube_api_key, channel_id, channel_name, video_id, video_title, video_url, video_seconds)



if __name__ == '__main__':
    es = connect_elasticsearch()
    if es is not None:
        create_index(es)
        for channel in get_channels():
            index_channel(es, channel['Name'], channel['Id'])
