import os
import re
import shutil
import tempfile
import asyncio
import subprocess
import logging
from flask import Flask, request, send_file, abort, after_this_request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Configure logging to capture detailed information about the app's operations
logging.basicConfig(
    level=logging.INFO,  # DEBUG for more verbosity
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    filename='server.log',  # Log to a file named server.log
    filemode='a', # Append mode to keep logs across restarts
)

# Get absolute directory path of the current script to build absolute paths reliably
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Cookie configuration path
COOKIE_FOLDER = "cookies"
COOKIE_FILE = "cookies.txt"
COOKIES_PATH = os.path.join(DIR_PATH, COOKIE_FOLDER, COOKIE_FILE)

# -compression_level 2 was removed because it’s not a valid option for MP3 encoding in ffmpeg and doesn’t affect the output, so it’s cleaner and safer to leave it out.
YTDL = [
    "yt-dlp", "--cookies", COOKIES_PATH,
    "-x", "--audio-format", "mp3", "--audio-quality", "0",
    "-N", "8", "--http-chunk-size", "10M",
    "--downloader", "aria2c",
    "--downloader-args", "aria2c:-x16 -j16 -k1M",
    "--postprocessor-args", "ffmpeg:-threads 4",
]

@app.get("/download")
# Refactored to use async/await for better performance
async def download():
    video_id_param = request.args.get("videoId", "")
    video_id_match = re.search(r"(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})", video_id_param)
    video_id = video_id_match.group(1) if video_id_match else video_id_param
    if not re.fullmatch(r"[0-9A-Za-z_-]{11}", video_id):
        # Log invalid video ID attempts
        logging.warning(f"Rejected invalid video ID: {video_id}")
        abort(400, "Invalid videoId")
    logging.info(f"Received valid request for video ID: {video_id}")
    workdir = tempfile.mkdtemp(dir="/dev/shm")
    outfile = os.path.join(workdir, f"{video_id}.mp3")
    @after_this_request
    def cleanup(response):
        # Manage cleanup of temporary files with error handling
        try:
            shutil.rmtree(workdir, ignore_errors=True)
            logging.info(f"Cleaned up temp dir for {video_id}")
        except Exception as e:
            logging.error(f"Error cleaning up temp dir for {video_id}: {e}")
        return response
    cmd = YTDL + ["-o", outfile, f"https://www.youtube.com/watch?v={video_id}"]
    try:
        # Manage subprocess with error handling and logging
        logging.info(f"Running yt-dlp for {video_id}")
        await asyncio.to_thread(
            subprocess.run,
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as exc:
        logging.error(f"Download failed for {video_id}: {exc}")
        abort(500, f"Download failed: {str(exc)}")
    except Exception as e:
        logging.error(f"Unexpected error during download for {video_id}: {e}")
        abort(500, "An unexpected error occurred")
    logging.info(f"Download and processing successful for {video_id}")
    return send_file(outfile, as_attachment=True, download_name=f"{video_id}.mp3")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)