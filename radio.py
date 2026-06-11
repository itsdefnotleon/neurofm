import os
import random
import subprocess
import urllib.parse
import requests
import json
import datetime

# ----------------------------
# LOAD CONFIG
# ----------------------------
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

ICECAST = config["icecast"]
FOLDERS = config["folders"]
NEWS = config["news"]

STATE_FILE = "status.json"
SUPPORTED = (".mp3", ".wav", ".ogg")

news_played_hour = -1


# ----------------------------
# STATE (dashboard sync)
# ----------------------------
def update_state(data):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except:
        pass


# ----------------------------
# FILE HANDLING
# ----------------------------
def get_files(folder):
    if not os.path.exists(folder):
        return []

    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(SUPPORTED)
    ]


def get_mode():
    hour = datetime.datetime.now().hour
    return "chill" if (hour >= 19 or hour < 7) else "normal"


def refresh_music(mode):
    folder = (
        FOLDERS["chill_music"]
        if mode == "chill"
        else FOLDERS["normal_music"]
    )
    return get_files(folder)


def refresh_tts():
    return get_files(FOLDERS["tts"])


# ----------------------------
# METADATA (Icecast now playing)
# ----------------------------
def update_metadata(artist, title):
    song = f"{artist} - {title}"

    url = (
        f"http://{ICECAST['host']}/admin/metadata"
        f"?mount={ICECAST['mount']}"
        f"&mode=updinfo"
        f"&song={urllib.parse.quote(song)}"
    )

    try:
        requests.get(
            url,
            auth=(ICECAST["username"], ICECAST["password"]),
            timeout=2
        )
    except:
        pass


def parse_name(file):
    name = os.path.splitext(os.path.basename(file))[0]

    if " - " in name:
        artist, title = name.split(" - ", 1)
    else:
        artist, title = "NeuroFM", name

    return artist, title


# ----------------------------
# ICECAST STREAM PIPE
# ----------------------------
ffmpeg = subprocess.Popen([
    "ffmpeg",
    "-re",
    "-f", "wav",
    "-i", "pipe:0",
    "-vn",
    "-c:a", "libmp3lame",
    "-b:a", "192k",
    "-f", "mp3",
    f"icecast://{ICECAST['username']}:{ICECAST['password']}@{ICECAST['host']}{ICECAST['mount']}"
], stdin=subprocess.PIPE)


# ----------------------------
# AUDIO SENDING
# ----------------------------
def send_file(path):
    proc = subprocess.Popen([
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", path,
        "-f", "wav",
        "-ac", "2",
        "-ar", "44100",
        "-"
    ], stdout=subprocess.PIPE)

    if not proc.stdout:
        return

    while True:
        chunk = proc.stdout.read(4096)
        if not chunk:
            break
        ffmpeg.stdin.write(chunk)

    ffmpeg.stdin.flush()


# ----------------------------
# NEWS STREAM
# ----------------------------
def play_news():
    proc = subprocess.Popen([
        "ffmpeg",
        "-re",
        "-i", NEWS["url"],
        "-f", "wav",
        "-"
    ], stdout=subprocess.PIPE)

    if not proc.stdout:
        return

    while True:
        chunk = proc.stdout.read(4096)
        if not chunk:
            break
        ffmpeg.stdin.write(chunk)

    ffmpeg.stdin.flush()


# ----------------------------
# QUEUE SYSTEM
# ----------------------------
music_queue = []

def refill_queue(music):
    if not music:
        return []

    q = music[:]
    random.shuffle(q)
    return q


# ----------------------------
# START
# ----------------------------
print("NeuroFM streaming engine starting...")

while True:
    now = datetime.datetime.now()
    mode = get_mode()

    music = refresh_music(mode)
    tts = refresh_tts()

    if not music_queue:
        music_queue = refill_queue(music)

    if now.hour != news_played_hour:
        news_played_hour = now.hour

    # ----------------------------
    # NEWS BREAK
    # ----------------------------
    if (
        NEWS["enabled"]
        and mode == "normal"
        and now.minute == NEWS["minute"]
        and news_played_hour == now.hour
    ):
        print("NEWS BREAK")

        update_state({
            "mode": "news",
            "artist": "Sky News",
            "title": "Live Bulletin"
        })

        update_metadata("Sky News", "Live Bulletin")
        play_news()

        news_played_hour = -1
        continue

    # ----------------------------
    # MUSIC PLAYBACK
    # ----------------------------
    if not music_queue:
        continue

    song = music_queue.pop()
    artist, title = parse_name(song)

    print("PLAY:", artist, "-", title)

    update_state({
        "mode": mode,
        "artist": artist,
        "title": title,
        "file": os.path.basename(song)
    })

    update_metadata(artist, title)
    send_file(song)

    # ----------------------------
    # TTS SEGMENT
    # ----------------------------
    if tts:
        voice = random.choice(tts)
        print("TTS:", os.path.basename(voice))
        send_file(voice)
