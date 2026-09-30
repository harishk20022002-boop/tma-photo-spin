import os
import re
import requests
from pathlib import Path

# Configuration
UPLOAD_FOLDER = './pending_uploads'
HTML_FILE_PATH = './index.html'
CATBOX_API_URL = "https://catbox.moe/user/api.php"

def upload_to_catbox(file_path):
    print(f"Uploading {os.path.basename(file_path)}...")
    with open(file_path, 'rb') as f:
        response = requests.post(CATBOX_API_URL, data={"reqtype": "fileupload"}, files={"fileToUpload": f})
    return response.text if response.status_code == 200 else None

def update_html_file(title, pic_url, zip_url):
    with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    existing_ids = [int(i) for i in re.findall(r"id:\s*(\d+)", content)]
    next_id = max(existing_ids) + 1 if existing_ids else 1

    new_entry = f"            {{ id: {next_id}, title: '{title}', image: '{pic_url}', downloadUrl: '{zip_url}', category: 'Daily Asset' }},\n"
    new_content = content.replace("const assets = [", f"const assets = [\n{new_entry}", 1)

    with open(HTML_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Added '{title}' to HTML")

def main():
    if not os.path.exists(UPLOAD_FOLDER):
        print("No pending_uploads folder found.")
        return

    posts = {}
    for file in os.listdir(UPLOAD_FOLDER):
        base = Path(file).stem
        ext = Path(file).suffix.lower()
        if base not in posts:
            posts[base] = {}
        if ext == '.zip':
            posts[base]['zip'] = os.path.join(UPLOAD_FOLDER, file)
        elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
            posts[base]['pic'] = os.path.join(UPLOAD_FOLDER, file)

    for post_name, files in posts.items():
        if 'zip' in files and 'pic' in files:
            pic_url = upload_to_catbox(files['pic'])
            zip_url = upload_to_catbox(files['zip'])
            
            if pic_url and zip_url:
                update_html_file(post_name.replace('-', ' ').title(), pic_url, zip_url)
                # Delete files so they aren't processed again tomorrow
                os.remove(files['zip'])
                os.remove(files['pic'])

if __name__ == "__main__":
    main()
