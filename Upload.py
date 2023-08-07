import httplib2
import os
import random
import time
import os, pickle
import json
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from Download import download_video
from oauth2client.tools import argparser, run_flow
from pytube import YouTube
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from Telegram import Send_Notification

httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def remove_links_from_paragraph(para):
    try :
        paragraph = str(para) 
        if not isinstance(paragraph, (str, bytes)):
            raise TypeError("Input should be a string or bytes-like object.")
        if isinstance(paragraph, bytes):
            paragraph = paragraph.decode('utf-8')
        url_pattern = r'https?://\S+|www\.\S+'
        cleaned_paragraph = re.sub(url_pattern, '', paragraph)
        return cleaned_paragraph
    except : 
        return None

def youtube_authenticate(pickle_files):
    pickle_file = pickle_files[0]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    creds = None
    if os.path.exists(pickle_file):
        with open(pickle_file, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(pickle_file, "wb") as token:
            pickle.dump(creds, token)
    return build(api_service_name, api_version, credentials=creds)


def initialize_upload(youtube, video_data,File_path):
    description_data = remove_links_from_paragraph(video_data.get('description', 'Test Description'))
    tags = video_data.get('tags', 'comedy')
    body = dict(
        snippet=dict(
            title=video_data.get('title', 'Test Title'),
            description=description_data,
            tags=tags,
            categoryId=video_data.get('category_id', '22')
        ),
        status=dict(
            privacyStatus=video_data.get('privacyStatus', 'private'),
            selfDeclaredMadeForKids = False
        )
    )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(File_path, chunksize=-1, resumable=True)
    )

    ID = resumable_upload(insert_request)
    return ID




def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print ("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
            print ("Video id '%s' was successfully uploaded." % response['id'])
            video_id = response['id']
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e
    
    if video_id:
        with open('video_id.txt', 'w') as file:
            file.write(video_id)
    if error is not None:
      print (error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print ("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def update_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def upload(file_name) :
    pickle_files = ["token.pickle", "token_.pickle", "token__.pickle"]
    try:
        file_path = f"Youtube Videos Meta Data/{file_name}.json"
        data = load_json_file(file_path)
    except FileNotFoundError:
        print("The 'video_data.json' file does not exist or cannot be found.")
        exit()
    video_data  = data[0]
    video_id = video_data['video_id']
    title = video_data['title']
    video_link = 'https://www.youtube.com/watch?v='+video_id
    video_path = download_video(video_link)
    if video_path:
        print("Video downloaded and saved at:", video_path)
    else:
        print("Failed to download the video:", video_id)
    print(video_path)
    while pickle_files:
        youtube = youtube_authenticate(pickle_files)
        try:
            li = initialize_upload(youtube,video_data, video_path)
            try :
                Send_Notification(Original_link=video_link, Original_title=title, Uploade_link=li, Channel_from=file_name)
            except : 
                pass
            data.pop(0)
            update_json_file(file_path, data)
            break
        except HttpError as e:
            data.pop(0)
            update_json_file(file_path, data)
            print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            if e.resp.status == 403 and "quotaExceeded" in e.content:
                pickle_files.pop(0)
                if not pickle_files:
                    print("All pickle files exhausted. Upload failed.")
                    break
            else:
                break
