import os
import shutil
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json

# Define the folder IDs and base URL for the Google Drive folder
GFX_FOLDER_ID = '1lU5pvyiRtd6D5Ho_3-1vbXXLeB0jrxry'
SECTORS_FOLDER_ID = '15Cb9UUym3Y5uwWrb1Rc4TDRht3dQMQ11'
BASE_URL = 'https://drive.google.com/drive/folders/'

def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

def fetch_file_links(folder_id):
    folder_url = urljoin(BASE_URL, folder_id)
    response = requests.get(folder_url)
    if response.status_code != 200:
        print(f"Failed to access folder: {folder_id}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts:
        if 'window.viewerData' in script.text:
            data = script.text.split('window.viewerData = ')[1].split(';')[0]
            data = json.loads(data)
            break
    
    files = []
    for entry in data['entries']:
        if entry['type'] == 'file':
            files.append({
                'name': entry['title'],
                'id': entry['id'],
                'download_url': f"https://drive.google.com/uc?export=download&id={entry['id']}"
            })
    return files

def download_file(file_info, destination_folder):
    response = requests.get(file_info['download_url'], stream=True)
    if response.status_code == 200:
        file_path = os.path.join(destination_folder, file_info['name'])
        with open(file_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print(f"Downloaded {file_info['name']}")
    else:
        print(f"Failed to download {file_info['name']}")

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

def update_local_folder(folder_id, local_path):
    clear_folder(local_path)
    files = fetch_file_links(folder_id)
    for file_info in files:
        download_file(file_info, local_path)

def main():
    script_dir = get_script_directory()
    local_gfx_folder = os.path.join(script_dir, 'GFX')
    local_sectors_folder = os.path.join(script_dir, 'sectors')
    
    update_local_folder(GFX_FOLDER_ID, local_gfx_folder)
    update_local_folder(SECTORS_FOLDER_ID, local_sectors_folder)

    print('Folders updated successfully!')

if __name__ == '__main__':
    main()
