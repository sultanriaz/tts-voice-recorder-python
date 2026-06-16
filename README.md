# 🎙️ TTS & Voice Recorder

A complete **Text-to-Speech** and **Voice Recording** system with:
- Desktop GUI (Tkinter)
- Web Interface (Flask)
- CLI menu
- English & Urdu TTS support
- Offline (pyttsx3) and Online (Google TTS) engines

---

## 📁 Project Structure

```
tts_project/
├── main.py              ← Entry point (CLI / GUI / Web launcher)
├── tts_module.py        ← TTS functions (online + offline)
├── recorder_module.py   ← Microphone recording & playback
├── gui.py               ← Tkinter desktop GUI
├── web_app.py           ← Flask web application
├── requirements.txt     ← Python dependencies
├── templates/
│   └── index.html       ← Flask HTML template
├── static/
│   └── audio/           ← Generated audio files (auto-created)
└── output/              ← Desktop-app audio output (auto-created)
```

---

## ⚙️ Installation

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> **Windows note — PyAudio:**
> If `pip install PyAudio` fails, install the pre-built wheel:
> ```
> pip install pipwin
> pipwin install pyaudio
> ```
> Or download the `.whl` from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

> **macOS note:**
> ```
> brew install portaudio
> pip install pyaudio
> ```

> **Linux note:**
> ```
> sudo apt-get install python3-pyaudio portaudio19-dev
> ```

---

## 🚀 Running the Project

### Interactive CLI menu
```bash
python main.py
```

### Desktop GUI (Tkinter)
```bash
python main.py --gui
# or directly:
python gui.py
```

### Web App (Flask)
```bash
python main.py --web
# or directly:
python web_app.py
```
Then open **http://127.0.0.1:5000** in your browser.

Custom port:
```bash
python main.py --web --port 8080
```

---

## 🌐 Languages Supported (Online/Google TTS)

| Language | Code |
|----------|------|
| English  | en   |
| Urdu     | ur   |
| Arabic   | ar   |
| French   | fr   |
| German   | de   |
| Spanish  | es   |
| Hindi    | hi   |

---

## 🛠️ Key Features

| Feature | Details |
|---------|---------|
| Online TTS | Google TTS via gTTS — supports Urdu |
| Offline TTS | pyttsx3 — uses system voices, works without internet |
| Speech rate | Adjustable 50–300 wpm (offline mode) |
| Volume | Adjustable 0.0 – 1.0 (offline mode) |
| Voice selection | All installed system voices (offline mode) |
| Recording | WAV · 44100 Hz · 16-bit · Mono |
| Playback | pygame (MP3 + WAV) with pyaudio fallback |
| Save dialogs | "Save As" dialog in desktop GUI |
| Download | Download buttons in web interface |

---

## 📋 Requirements

- Python 3.10+
- Internet connection (for online TTS only)
- Working microphone (for recording)
- Speakers / headphones (for playback)
