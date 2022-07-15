import time
import os
import cv2  # opencv
import numpy as np
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
import ffmpeg

from googleapiclient.http import MediaFileUpload
from Google import Create_Service  # Google.Py
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

class NewSampleEventHandler(PatternMatchingEventHandler):
    def __init__(self, folderid=None, **kwargs):
        super().__init__(**kwargs)

        # the google drive folder id to store mp4s in
        self.folder_id = folderid

    def on_any_event(self, event):
        # for testing purposes, log every event
        logging.info(event)
        pass

    def on_created(self, event):
        # when a new mp4 file is created, process the previous one
        # this avoids any potential issues with processing a newly
        # created png file before it is finished being written to

        sampleSend([event.src_path], "", self.folder_id)
        print("Sample uploaded")
        os.remove(event.src_path)
        print("Local sample deleted")

def getSamples(path, target_drive):
    # Function that repeatedly polls a directory looking for
    # new mp4s (samples from livestream) and uses an observer to
    # process them when they are created, and delete them when the
    # next sampled frame is available.  Modified from quickstart example in
    # Python watchdog library documentation
    # path - folder to watch for new mp4s

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = NewSampleEventHandler(patterns=['*.mp4'],
                                         folderid=target_drive,
                                         ignore_directories=True)

    # Create, configure, and start the observer
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    print("Ready to upload")
    # while loop so the user is able to interrupt execution
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def sampleSend(in_file, output_path, folder_id):

    CLIENT_SECRET_FILE = 'client_secret_drive.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    #file_name = ['input.mp4']
    mime_types = ['video/mp4']

    for in_file, mime_types in zip(in_file, mime_types):
        file_metadata = {
            'name': f"{time.time()}{in_file}",
            'parents': [folder_id]
        }

        medias = MediaFileUpload('{0}{1}'.format(output_path, in_file),
                                 mimetype=mime_types)

        service.files().create(
            body=file_metadata,
            media_body=medias,
            fields='id'
        ).execute()



if __name__ == "__main__":
    getSamples("finishedSamples/", target_drive='---PUT GOOGLEDRIVE FOLDER ID HERE---')
