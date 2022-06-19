from googleapiclient.http import MediaFileUpload
from Google import Create_Service # Google.Py
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Google Authorization
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# Google Drive API
CLIENT_SECRET_FILE = 'client_secret_drive.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

folder_id = '1QRUav2SWJ3gqo55aHVGDIWi7Y-o-Zzif'
file_name = ['input.mp4']
mime_types = ['video/mp4']
pathway = ['C:/Users/fireb/PycharmProjects/extract_metrics/']

# upload file
for file_name, mime_types in zip(file_name, mime_types):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media_content = MediaFileUpload('C:/Users/fireb/PycharmProjects/extract_metrics/{0}'.format(file_name),
                                    mimetype=mime_types)

    file = service.files().create(
        body=file_metadata,
        media_body=media_content,
        fields='id'
    ).execute()
