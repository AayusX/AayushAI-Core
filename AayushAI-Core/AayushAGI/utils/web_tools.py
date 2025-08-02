import requests
from bs4 import BeautifulSoup
import re


def youtube_second_video_url(query):
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Use regex to find "/watch?v=" links
        matches = re.findall(r'href=\"(/watch\?v=[\w-]+)\"', response.text)
        video_ids = []
        for m in matches:
            if m not in video_ids:
                video_ids.append(m)

        if len(video_ids) >= 2:
            return "https://www.youtube.com" + video_ids[1]
        elif video_ids:
            return "https://www.youtube.com" + video_ids[0]
        else:
            return None
    except Exception as e:
        print(f"[YouTube Error]: {e}")
        return None


def google_search(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.select("a"):
            href = a.get("href")
            if href and href.startswith("/url?q="):
                clean_url = href.split("/url?q=")[1].split("&")[0]
                if "google.com" not in clean_url:
                    return clean_url

        return None
    except Exception as e:
        print(f"[Google Search Error]: {e}")
        return None
