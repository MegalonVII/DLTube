from flask import Flask, render_template, request, send_file
import os
import yt_dlp as youtube_dl
from urllib.parse import urlparse, parse_qs
from pytz import timezone
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    invalid_url = False
    if request.method == "POST":
        youtube_url = request.form["youtube_url"]
        selected_format = request.form["format"]
        if is_valid_url(youtube_url):
            file = download_media(youtube_url, selected_format)
            try:
                return send_file(file, as_attachment=True)
            finally:
                os.remove(file)
        else:
            invalid_url = True
    else:
        invalid_url = False
    return render_template("docs/index.html", invalid_url=invalid_url)

def is_valid_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == "www.youtube.com" and parsed_url.path.startswith("/watch"):
        video_id = parse_qs(parsed_url.query).get("v")
        if video_id and len(video_id[0]) == 11:
            return True
    elif parsed_url.netloc == "youtu.be":
        video_id = parsed_url.path[1:]
        if video_id and len(video_id) == 11:
            return True
    return False

def download_media(url, selected_format):
    ydl_opts = {
        "format": "bestaudio/best" if selected_format == "mp3" else "best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ] if selected_format == "mp3" else [],
        "outtmpl": "%(title)s.%(ext)s"
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        media_file = ydl.prepare_filename(info_dict)
        base, ext = os.path.splitext(media_file)
        output_file = base + f".{selected_format}"

    return output_file

def get_login_time(tz: str) -> str:
    hour = int(datetime.now(timezone(tz)).strftime("%H"))
    if hour >= 12:
        AMorPM = "PM"
        if hour >= 13:
            hour -= 12
    elif hour < 12:
        AMorPM = "AM"
        if hour == 0:
            hour = 12
    return f"\nLogged in at {datetime.now(timezone(tz)).strftime('%m/%d/%Y')}, {hour}:{datetime.now(timezone(tz)).strftime('%M:%S')} {AMorPM}\nTimezone: {tz}\n"

print(get_login_time('US/Eastern'))
app.run(host='0.0.0.0', port=80)
