import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# 认证并建立服务
def authenticate_gdrive():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    return service


# 上传文件
def upload_file_to_gdrive(service, file_path, folder_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]  # 指定目标文件夹的ID
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file["id"]} uploaded successfully.')


# 批量上传文件
def upload_files_from_txt(txt_file, folder_id):
    service = authenticate_gdrive()

    with open(txt_file, 'r') as file:
        file_paths = file.readlines()

    # 清除换行符并上传文件
    for file_path in file_paths:
        file_path = file_path.strip()  # 去除每行的换行符
        if os.path.exists(file_path):
            upload_file_to_gdrive(service, file_path, folder_id)
        else:
            print(f"File not found: {file_path}")


# 用户输入txt文件路径和Google Drive文件夹ID
txt_file = 'files.txt'  # 存放文件路径的txt文件
folder_id = 'your-folder-id-here'  # 替换为Google Drive目标文件夹的ID

upload_files_from_txt(txt_file, folder_id)
