# Multilingual Text-to-Speech & Voice Recorder Suite

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-Desktop_GUI-1E293B?style=for-the-badge)
![gTTS](https://img.shields.io/badge/gTTS-Google_TTS-4285F4?style=for-the-badge)
![pyttsx3](https://img.shields.io/badge/pyttsx3-Offline_TTS-0284C7?style=for-the-badge)
![PyAudio](https://img.shields.io/badge/PyAudio-Audio_Stream-10B981?style=for-the-badge)

A multi-interface audio engineering toolkit providing online and offline text-to-speech synthesis (with specialized Urdu language support) paired with PyAudio microphone recording across CLI, Tkinter GUI, and Flask web interfaces.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    UserInterface["User Interface Layer"] --> CLI["Command-Line Interface (main.py)"]
    UserInterface --> Desktop["Tkinter Desktop GUI (gui.py)"]
    UserInterface --> Web["Flask Web Application (web_app.py)"]
    
    CLI --> TaskRouter{"Requested Mode"}
    Desktop --> TaskRouter
    Web --> TaskRouter
    
    TaskRouter -->|Speech Synthesis| TTSModule["TTS Module (tts_module.py)"]
    TTSModule --> OnlineTTS["gTTS Engine (Online / Urdu / Multilingual)"]
    TTSModule --> OfflineTTS["pyttsx3 SAPI5/NSSpeech (Zero-Latency Offline)"]
    OnlineTTS --> AudioOutput["Audio Output & Export (MP3 / WAV)"]
    OfflineTTS --> AudioOutput
    
    TaskRouter -->|Voice Recording| RecModule["Voice Recorder (recorder_module.py)"]
    RecModule --> StreamCapture["PyAudio Microphone Stream"]
    StreamCapture --> WaveEncoder["WAV Chunk Buffering & Encoding"]
    WaveEncoder --> SavedRecording["Saved Audio Files (/recordings)"]
```

---

## 🔬 Core Capabilities

- **Tri-Interface Design:** Access identical synthesis and recording functionality through interactive CLI, responsive Tkinter desktop GUI, or a lightweight Flask web application.
- **Dual-Engine Speech Synthesis:**
  - **Online Synthesis (`gTTS`):** Natural speech generation supporting Urdu (`ur`) and English.
  - **Offline Synthesis (`pyttsx3`):** Zero-latency local system speech synthesis without network dependency.
- **PyAudio Microphone Stream:** Chunked audio recording with custom sample rate and channel configuration, exporting directly to standardized WAV format.

---

## 📁 Repository Structure

```
tts-voice-recorder-python/
├── main.py                # Command-line interface entrypoint
├── gui.py                 # Tkinter desktop interface
├── web_app.py             # Flask web application
├── tts_module.py          # Unified gTTS & pyttsx3 speech synthesizer
├── recorder_module.py     # PyAudio recording and file writer
└── requirements.txt       # Dependencies manifest
```

---

## 🚀 Quickstart CLI Commands

### 1. Installation
```bash
git clone https://github.com/sultanriaz/tts-voice-recorder-python.git
cd tts-voice-recorder-python
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Run Modes
- **Launch Desktop GUI:**
  ```bash
  python gui.py
  ```
- **Launch Web Interface:**
  ```bash
  python web_app.py
  ```
- **Run Command-Line Interface:**
  ```bash
  python main.py
  ```
