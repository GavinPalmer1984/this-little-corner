import os
import sys
import requests
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# YouTube Data API key
API_KEY = os.getenv('YOUTUBE_API_KEY')

def get_channel_info(channel_url):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Extract the handle or channel ID from the URL
    if '@' in channel_url:
        handle = channel_url.split('/')[-1]

        # Search for the channel by handle
        response = youtube.search().list(
            part='snippet',
            q=handle,
            type='channel',
            maxResults=1
        ).execute()

        if 'items' not in response or not response['items']:
            raise ValueError('Channel not found.')

        channel = response['items'][0]
        channel_name = channel['snippet']['channelTitle']
        channel_id = channel['snippet']['channelId']
    else:
        raise ValueError('Invalid channel URL.')

    return channel_name, channel_id

def get_videos_for_channel(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Get the uploads playlist ID
    response = youtube.channels().list(
        id=channel_id,
        part='contentDetails'
    ).execute()

    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Retrieve videos from the playlist
    video_ids = []
    next_page_token = None

    while True:
        playlist_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

def fetch_transcript(video_id, channel_folder):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Save transcript to file
        transcript_file = os.path.join(channel_folder, f"{video_id}.txt")
        with open(transcript_file, 'w', encoding='utf-8') as f:
            for entry in transcript:
                f.write(f"{entry['start']} - {entry['duration']}: {entry['text']}\n")
        print(f"Transcript saved for video {video_id}")
    except Exception as e:
        print(f"Could not fetch transcript for video {video_id}: {str(e)}")

def main(channel_url):
    # Get channel information
    channel_name, channel_id = get_channel_info(channel_url)
    print(f"Channel Name: {channel_name}")
    print(f"Channel ID: {channel_id}")

    # Set up data folder
    data_folder = os.path.join("src", "data", "raw_transcripts", channel_id)
    os.makedirs(data_folder, exist_ok=True)

    # Get all videos for the channel
    video_ids = get_videos_for_channel(channel_id)
    print(f"Found {len(video_ids)} videos.")

    # Fetch transcripts for each video
    for video_id in video_ids:
        transcript_file = os.path.join(data_folder, f"{video_id}.txt")
        if not os.path.exists(transcript_file):
            fetch_transcript(video_id, data_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/utils/scrape_youtube_channel.py <youtube_channel_url>")
        sys.exit(1)

    channel_url = sys.argv[1]
    main(channel_url)
