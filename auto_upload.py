import os, json, time, schedule
from TikTokApi import TikTokApi
import requests

# Load config
with open("config.json") as f:
    config = json.load(f)

TIKTOK_USERS = config["tiktok_usernames"]
PAGE_ID = config["page_id"]
FB_TOKEN = config["access_token"]

# Load uploaded video IDs
if os.path.exists("uploaded.json"):
    with open("uploaded.json") as f:
        uploaded = set(json.load(f))
else:
    uploaded = set()

def save_uploaded():
    with open("uploaded.json", "w") as f:
        json.dump(list(uploaded), f)

def download_and_upload(user):
    print(f"🔍 Checking @{user}...")
    api = TikTokApi.get_instance()
    videos = api.by_username(user, count=20)

    for video in videos:
        video_id = video["id"]
        if video_id in uploaded:
            continue

        duration = video.get("video", {}).get("duration", 999)
        if duration > 90:
            continue

        print(f"⬇️  Downloading video {video_id}...")
        video_bytes = api.get_video_by_tiktok(video)
        file_path = f"{video_id}.mp4"
        with open(file_path, "wb") as f:
            f.write(video_bytes)

        print(f"📤 Uploading to Facebook Page {PAGE_ID}...")
        url = f"https://graph.facebook.com/{PAGE_ID}/videos"
        files = {"source": open(file_path, "rb")}
        data = {
            "access_token": FB_TOKEN,
            "description": f"Video dari TikTok @{user}"
        }
        response = requests.post(url, files=files, data=data)
        print("✅ Response:", response.json())

        uploaded.add(video_id)
        save_uploaded()
        os.remove(file_path)

def job():
    for user in TIKTOK_USERS:
        try:
            download_and_upload(user)
        except Exception as e:
            print(f"❌ Error processing {user}: {e}")

schedule.every(60).minutes.do(job)

print("🚀 Bot dimulai. Menunggu jadwal upload...")
while True:
    schedule.run_pending()
    time.sleep(1)