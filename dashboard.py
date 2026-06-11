from flask import Flask, jsonify, Response, send_from_directory
import os
import json
import requests
import datetime

app = Flask(__name__)

# ----------------------------
# CONFIG
# ----------------------------
STATE_FILE = "status.json"
ICECAST_URL = "http://127.0.0.1:8000/neurofm"
LOGO = "https://cdn.junipercreates.com/marketing-sandbox/images/colored_1763651518889.png"


# ----------------------------
# STATE HANDLING
# ----------------------------
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"mode": "idle"}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"mode": "idle"}


# ----------------------------
# SCHEDULE LOGIC
# ----------------------------
def get_schedule_block():
    hour = datetime.datetime.now().hour

    if 7 <= hour < 19:
        return {
            "name": "NeuroFM Main Music",
            "time": "07:00 – 19:00",
            "active": "main"
        }
    else:
        return {
            "name": "NeuroFM At Night",
            "time": "19:00 – 07:00",
            "active": "night"
        }


# ----------------------------
# ASSETS
# ----------------------------
@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory("assets", filename)


# ----------------------------
# STREAM PROXY
# ----------------------------
@app.route("/neurofm")
def stream():
    def generate():
        try:
            with requests.get(ICECAST_URL, stream=True, timeout=10) as r:
                r.raise_for_status()

                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
        except:
            yield b""

    return Response(generate(), content_type="audio/mpeg")


# ----------------------------
# STATE API
# ----------------------------
@app.route("/state")
def state():
    return jsonify(load_state())


# ----------------------------
# HTML (PUBLIC UI)
# ----------------------------
PUBLIC_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<title>NeuroFM</title>

<link rel="icon" href="/assets/favicon.ico">

<style>
body {{
    margin: 0;
    font-family: system-ui;
    background: radial-gradient(circle at top, #1b1b2f, #000);
    color: white;
}}

.header {{
    display: flex;
    justify-content: space-between;
    padding: 20px 40px;
    align-items: center;
}}

.logo {{
    height: 42px;
}}

.badge {{
    padding: 6px 12px;
    background: #6c5ce7;
    border-radius: 999px;
    font-size: 12px;
}}

.container {{
    display: flex;
    justify-content: center;
    padding: 40px;
}}

.card {{
    width: min(900px, 95%);
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 30px;
}}

.title {{
    font-size: 40px;
    font-weight: 700;
}}

.sub {{
    color: #aaa;
}}

.now {{
    font-size: 22px;
    margin-top: 20px;
}}

.schedule {{
    margin-top: 30px;
    padding: 20px;
    border-radius: 16px;
    background: rgba(255,255,255,0.05);
}}

.block {{
    padding: 10px;
    border-radius: 10px;
    margin-top: 10px;
    background: rgba(255,255,255,0.05);
}}

.active {{
    border: 1px solid #6c5ce7;
    background: rgba(108,92,231,0.2);
}}
</style>
</head>

<body>

<div class="header">
    <img class="logo" src="{LOGO}">
    <div class="badge">LIVE</div>
</div>

<div class="container">
<div class="card">

    <div class="title">NeuroFM</div>
    <div class="sub">AI-powered radio stream</div>

    <div id="now" class="now">Loading...</div>

    <audio controls autoplay>
        <source src="/neurofm" type="audio/mpeg">
    </audio>

    <div class="schedule">
        <h3>Schedule</h3>

        <div id="mainBlock" class="block">
            ☀️ 07:00 – 19:00<br>
            NeuroFM Main Music
        </div>

        <div id="nightBlock" class="block">
            🌙 19:00 – 07:00<br>
            NeuroFM At Night
        </div>
    </div>

</div>
</div>

<script>
async function update() {{
    const res = await fetch('/state?t=' + Date.now());
    const data = await res.json();

    if (data.mode === "music" || data.mode === "chill") {{
        document.getElementById('now').innerText =
            data.artist + " — " + data.title;
    }} else if (data.mode === "news") {{
        document.getElementById('now').innerText =
            "Sky News Bulletin";
    }} else {{
        document.getElementById('now').innerText =
            "Station Idle";
    }}

    const hour = new Date().getHours();

    if (hour >= 7 && hour < 19) {{
        document.getElementById('mainBlock').classList.add('active');
        document.getElementById('nightBlock').classList.remove('active');
    }} else {{
        document.getElementById('nightBlock').classList.add('active');
        document.getElementById('mainBlock').classList.remove('active');
    }}
}}

setInterval(update, 1500);
update();
</script>

</body>
</html>
"""


ADMIN_HTML = PUBLIC_HTML.replace("LIVE", "STUDIO")


# ----------------------------
# ROUTES
# ----------------------------
@app.route("/")
def home():
    return PUBLIC_HTML


@app.route("/admin")
def admin():
    return ADMIN_HTML


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
