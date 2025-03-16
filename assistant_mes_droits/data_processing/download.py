import requests


def download_zip(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content
