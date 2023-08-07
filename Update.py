# Author - Uma Abu
# Description - This file contains the main application code for the Flask app

import httplib2
import flask
from apiclient.errors import HttpError
from flask import send_file
import requests
from googleapiclient.http import MediaFileUpload
import urllib.parse as p
import os, pickle
from PIL import Image, ImageFont, ImageDraw 
from oauth2client.client import flow_from_clientsecrets

from apiclient.discovery import build
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.tools import argparser, run_flow
from oauth2client.file import Storage
import httplib2
import os
import sys


CLIENT_SECRETS_FILE = "google-credentials.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def update_view_count_and_thumbnail():
  pickle_files = ["token.pickle", "token_.pickle", "token__.pickle"]
  video_id = read_video_id_from_file()
  print("Updating Video Status")
  while pickle_files:
    youtube = youtube_authenticate(pickle_files)
    try: 
        title_update_request = youtube.videos().update(
            part='status',
            body={
                "id": video_id,
                "status": {
                    "privacyStatus": "public"
                }
            }
        )
        title_update_response = title_update_request.execute()
        update_responses = {}
        print("Successfully Updated Video Title and Thumbnail")
        break
    except HttpError as e:
            print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            if e.resp.status == 403 and "quotaExceeded" in e.content:
                pickle_files.pop(0)
                if not pickle_files:
                    print("All pickle files exhausted. Upload failed.")
                    break
            else:
                break



def read_video_id_from_file(filename='video_id.txt'):
    try:
        with open(filename, 'r') as file:
            video_id = file.readline().strip()
            return video_id
    except FileNotFoundError:
        print(f"File '{filename}' not found. No video ID available.")
        return None
    except Exception as e:
        print(f"Error occurred while reading the file: {e}")
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
