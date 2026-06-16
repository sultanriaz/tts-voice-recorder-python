"""
web_app.py
Flask web interface for the TTS & Voice Recorder system.
Provides a REST API consumed by templates/index.html.
"""

import os
import uuid
import threading
from flask import (
    Flask, render_template, request, jsonify,
    send_file, send_from_directory,
)

from tts_module import generate_tts, get_supported_languages
from recorder_module import AudioRecorder

# ─────────────────────────────────────────────
#  App setup
# ─────────────────────────────────────────────

BASE_DIR    = os.path.dirname(__file__)
STATIC_DIR  = os.path.join(BASE_DIR, "static", "audio")
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

# Active recorders keyed by session token
_recorders: dict[str, AudioRecorder] = {}
_lock = threading.Lock()


# ─────────────────────────────────────────────
#  Routes – Pages
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main HTML page."""
    languages = list(get_supported_languages().keys())
    return render_template("index.html", languages=languages)


# ─────────────────────────────────────────────
#  Routes – TTS API
# ─────────────────────────────────────────────

@app.route("/api/tts", methods=["POST"])
def api_tts():
    """
    Generate TTS audio from posted JSON.

    Request JSON:
        text        : str  – Text to synthesize.
        language    : str  – Language name (default "English").
        engine      : str  – "online" | "offline" (default "online").
        slow        : bool – Slow speech (online only, default False).

    Response JSON:
        status      : "ok" | "error"
        filename    : str  – Filename to use with /api/download/<filename>
        message     : str  – Error description (only on error)
    """
    data = request.get_json(force=True, silent=True) or {}

    text     = (data.get("text") or "").strip()
    language = data.get("language", "English")
    engine   = data.get("engine", "online")
    slow     = bool(data.get("slow", False))

    if not text:
        return jsonify(status="error", message="Text cannot be empty."), 400

    filename    = f"tts_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(STATIC_DIR, filename)

    try:
        generate_tts(
            text=text,
            output_path=output_path,
            engine_type=engine,
            language=language,
            slow=slow,
        )
    except Exception as exc:
        return jsonify(status="error", message=str(exc)), 500

    return jsonify(status="ok", filename=filename)


# ─────────────────────────────────────────────
#  Routes – Download
# ─────────────────────────────────────────────

@app.route("/api/download/<filename>")
def api_download(filename: str):
    """
    Stream an audio file as a download.

    URL param:
        filename : Filename returned by /api/tts or /api/recorder/stop.
    """
    safe_name = os.path.basename(filename)
    file_path = os.path.join(STATIC_DIR, safe_name)

    if not os.path.exists(file_path):
        return jsonify(status="error", message="File not found."), 404

    return send_file(file_path, as_attachment=True, download_name=safe_name)


@app.route("/api/stream/<filename>")
def api_stream(filename: str):
    """Stream audio inline (for the <audio> player in the browser)."""
    safe_name = os.path.basename(filename)
    return send_from_directory(STATIC_DIR, safe_name)


# ─────────────────────────────────────────────
#  Routes – Recorder API
# ─────────────────────────────────────────────

@app.route("/api/recorder/start", methods=["POST"])
def api_recorder_start():
    """
    Start a new recording session.

    Response JSON:
        status  : "ok" | "error"
        token   : str  – Session token to use with /stop.
    """
    token    = uuid.uuid4().hex
    recorder = AudioRecorder()
    try:
        recorder.start()
    except Exception as exc:
        return jsonify(status="error", message=str(exc)), 500

    with _lock:
        _recorders[token] = recorder

    return jsonify(status="ok", token=token)


@app.route("/api/recorder/stop", methods=["POST"])
def api_recorder_stop():
    """
    Stop the recording session and save the audio.

    Request JSON:
        token : str – Token returned by /start.

    Response JSON:
        status   : "ok" | "error"
        filename : str  – WAV filename to use with /download.
    """
    data  = request.get_json(force=True, silent=True) or {}
    token = data.get("token", "")

    with _lock:
        recorder = _recorders.pop(token, None)

    if recorder is None:
        return jsonify(status="error", message="Invalid or expired token."), 400

    filename    = f"rec_{uuid.uuid4().hex}.wav"
    output_path = os.path.join(STATIC_DIR, filename)

    try:
        recorder.stop(output_path)
    except Exception as exc:
        return jsonify(status="error", message=str(exc)), 500

    return jsonify(status="ok", filename=filename)


# ─────────────────────────────────────────────
#  Housekeeping
# ─────────────────────────────────────────────

def _cleanup_old_files(max_files: int = 50):
    """
    Remove old audio files if the output directory grows too large.
    Keeps the newest *max_files* files.
    """
    files = sorted(
        [os.path.join(STATIC_DIR, f) for f in os.listdir(STATIC_DIR)],
        key=os.path.getmtime,
    )
    for old in files[:-max_files]:
        try:
            os.remove(old)
        except OSError:
            pass


# ─────────────────────────────────────────────
#  Entry-point
# ─────────────────────────────────────────────

def launch(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Start the Flask development server."""
    _cleanup_old_files()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    launch(debug=True)
