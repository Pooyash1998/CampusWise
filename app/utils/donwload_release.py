import subprocess
import streamlit as st

def download_chromaDB():
    # GitHub repository details
    token = st.secrets["GITHUB_TOKEN"]  # Fine-grained personal access token
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")

    # The URL and headers from the working curl command
    asset_url = "https://api.github.com/repos/Pooyash1998/CampusWise/releases/assets/232984673"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/octet-stream'
    }

    # Construct the curl command
    curl_command = [
        "curl",
        "-L",  # Follow redirects
        "-#",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/octet-stream",
        "-o", "chroma.sqlite3", 
        asset_url
    ]
    try:
        result = subprocess.run(curl_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Download successful! Output: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"Download failed: {e.stderr.decode()}")

if __name__ == "__main__":
    download_chromaDB()
