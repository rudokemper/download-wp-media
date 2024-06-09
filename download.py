import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse

def download_file(session, url, local_path):
    response = session.get(url, stream=True, timeout=10)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print(f"Downloaded: {local_path}")

def traverse_and_download(session, url, local_base_dir, visited):
    if url in visited:
        return
    visited.add(url)

    response = session.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.startswith('?') and not href.startswith('#'):
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            relative_path = os.path.relpath(parsed.path, '/wp-content/uploads/')
            if parsed.path.endswith('/'):
                traverse_and_download(session, full_url, local_base_dir, visited)
            else:
                path_parts = relative_path.split('/')
                if len(path_parts) >= 2:
                    year = path_parts[0]
                    month = path_parts[1]
                    filename = path_parts[-1]
                    new_filename = f"{year}_{month}_{filename}"
                    local_file_path = os.path.join(local_base_dir, new_filename)
                    download_file(session, full_url, local_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download files from HTTP directory recursively.')
    parser.add_argument('--domain', required=True, help='Base URL of the HTTP directory to download from.')
    parser.add_argument('--output', default='downloads', help='Local directory to save downloaded files.')
    args = parser.parse_args()

    base_url = f"http://{args.domain}/wp-content/uploads/"
    local_base_dir = args.output
    visited = set()
    
    with requests.Session() as session:
        traverse_and_download(session, base_url, local_base_dir, visited)
