

import argparse
import sys
import os


# ─────────────────────────────────────────────
#  CLI helpers
# ─────────────────────────────────────────────

def _banner():
    print("\n" + "═" * 56)
    print("  🎙️  TTS & Voice Recorder  —  Python Project")
    print("═" * 56)


def _menu():
    """Interactive text menu for quick testing without a GUI."""
    _banner()
    while True:
        print("""
  [1]  Text-to-Speech  (online, gTTS)
  [2]  Text-to-Speech  (offline, pyttsx3)
  [3]  Record audio    (microphone → WAV)
  [4]  Play audio file
  [5]  List available voices (offline)
  [6]  List available languages (online)
  [7]  Launch Desktop GUI  (Tkinter)
  [8]  Launch Web App      (Flask)
  [0]  Exit
""")
        choice = input("  Choice: ").strip()

        if choice == "1":
            _cli_online_tts()
        elif choice == "2":
            _cli_offline_tts()
        elif choice == "3":
            _cli_record()
        elif choice == "4":
            _cli_play()
        elif choice == "5":
            _cli_list_voices()
        elif choice == "6":
            _cli_list_languages()
        elif choice == "7":
            _launch_gui()
            break
        elif choice == "8":
            _launch_web()
            break
        elif choice == "0":
            print("  Goodbye! 👋")
            break
        else:
            print("  ⚠️  Invalid choice, try again.")


# ─────────────────────────────────────────────
#  CLI actions
# ─────────────────────────────────────────────

def _cli_online_tts():
    from tts_module import generate_tts
    text     = input("  Enter text: ").strip()
    language = input("  Language [English]: ").strip() or "English"
    slow     = input("  Slow speech? (y/n) [n]: ").strip().lower() == "y"
    out      = input("  Output file [output.mp3]: ").strip() or "output.mp3"

    print("  Generating…", end=" ", flush=True)
    path = generate_tts(text, out, engine_type="online",
                        language=language, slow=slow)
    print(f"✅  Saved to: {path}")


def _cli_offline_tts():
    from tts_module import generate_tts, get_available_voices

    voices = get_available_voices()
    if voices:
        print("  Available voices:")
        for v in voices:
            print(f"    [{v['index']}] {v['name']}")
        vi = int(input(f"  Voice index [0]: ").strip() or "0")
    else:
        vi = 0

    text = input("  Enter text: ").strip()
    rate = int(input("  Speech rate wpm [150]: ").strip() or "150")
    vol  = float(input("  Volume 0-1 [1.0]: ").strip() or "1.0")
    out  = input("  Output file [output_offline.wav]: ").strip() or "output_offline.wav"

    print("  Generating…", end=" ", flush=True)
    path = generate_tts(text, out, engine_type="offline",
                        rate=rate, volume=vol, voice_index=vi)
    print(f"✅  Saved to: {path}")


def _cli_record():
    from recorder_module import record_audio
    duration = float(input("  Recording duration (seconds) [5]: ").strip() or "5")
    out      = input("  Output WAV file [recording.wav]: ").strip() or "recording.wav"
    print(f"  Recording for {duration}s… (speak now)")
    path = record_audio(out, duration)
    print(f"✅  Saved to: {path}")


def _cli_play():
    from recorder_module import play_audio
    path = input("  File path to play: ").strip()
    if not os.path.exists(path):
        print(f"  ❌  File not found: {path}")
        return
    print("  Playing…")
    play_audio(path)
    print("  Done.")


def _cli_list_voices():
    from tts_module import get_available_voices
    voices = get_available_voices()
    if not voices:
        print("  No voices found (pyttsx3 may not be installed).")
        return
    print("\n  Offline voices:")
    for v in voices:
        print(f"    [{v['index']}] {v['name']}")


def _cli_list_languages():
    from tts_module import get_supported_languages
    langs = get_supported_languages()
    print("\n  Online (gTTS) supported languages:")
    for name, code in langs.items():
        print(f"    {name:12s}  →  {code}")


# ─────────────────────────────────────────────
#  GUI / Web launchers
# ─────────────────────────────────────────────

def _launch_gui():
    from gui import launch
    launch()


def _launch_web(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    from web_app import launch
    print(f"\n  🌐  Starting Flask server on http://127.0.0.1:{port}")
    print("     Press Ctrl+C to stop.\n")
    launch(host=host, port=port, debug=debug)


# ─────────────────────────────────────────────
#  Argument parsing
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="TTS & Voice Recorder — desktop GUI, web app, or CLI",
    )
    parser.add_argument("--gui",   action="store_true", help="Launch Tkinter GUI")
    parser.add_argument("--web",   action="store_true", help="Launch Flask web app")
    parser.add_argument("--host",  default="0.0.0.0",  help="Flask host (default 0.0.0.0)")
    parser.add_argument("--port",  type=int, default=5000, help="Flask port (default 5000)")
    parser.add_argument("--debug", action="store_true", help="Flask debug mode")

    args = parser.parse_args()

    if args.gui:
        _launch_gui()
    elif args.web:
        _launch_web(host=args.host, port=args.port, debug=args.debug)
    else:
        _menu()


if __name__ == "__main__":
    main()
