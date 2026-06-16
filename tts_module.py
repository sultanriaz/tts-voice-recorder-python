"""
tts_module.py
Handles all Text-to-Speech conversions using pyttsx3 (offline) and gTTS (online).
Supports English and Urdu languages, adjustable speed/volume, and multiple voices.
"""

import os
import pyttsx3
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile


# ─────────────────────────────────────────────
#  Offline TTS  (pyttsx3)
# ─────────────────────────────────────────────

def get_offline_engine(rate: int = 150, volume: float = 1.0, voice_index: int = 0):
    """
    Create and configure a pyttsx3 engine.

    Args:
        rate        : Speech rate in words-per-minute (default 150).
        volume      : Volume level 0.0 – 1.0 (default 1.0).
        voice_index : Index of the system voice to use (default 0).

    Returns:
        Configured pyttsx3 engine instance.
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    voices = engine.getProperty("voices")
    if voices and voice_index < len(voices):
        engine.setProperty("voice", voices[voice_index].id)

    return engine


def get_available_voices() -> list[dict]:
    """
    Return a list of available offline (pyttsx3) system voices.

    Returns:
        List of dicts with keys: index, id, name, languages.
    """
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    result = []
    for i, v in enumerate(voices):
        result.append({
            "index": i,
            "id": v.id,
            "name": v.name,
            "languages": v.languages,
        })
    engine.stop()
    return result


def speak_offline(text: str, rate: int = 150, volume: float = 1.0,
                  voice_index: int = 0) -> None:
    """
    Speak *text* aloud immediately via pyttsx3 (no file saved).

    Args:
        text        : Text to be spoken.
        rate        : Speech rate (wpm).
        volume      : Volume 0.0 – 1.0.
        voice_index : System voice index.
    """
    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    engine = get_offline_engine(rate, volume, voice_index)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def save_offline_tts(text: str, output_path: str, rate: int = 150,
                     volume: float = 1.0, voice_index: int = 0) -> str:
    """
    Convert *text* to speech offline and save as an audio file.

    pyttsx3 saves natively as .aiff on macOS or .wav/.mp3 depending on driver.
    We save to a temp .wav then let the caller handle it.

    Args:
        text        : Text to synthesize.
        output_path : Destination file path (should end in .mp3 or .wav).
        rate        : Speech rate (wpm).
        volume      : Volume 0.0 – 1.0.
        voice_index : System voice index.

    Returns:
        Absolute path of the saved file.
    """
    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    engine = get_offline_engine(rate, volume, voice_index)

    # pyttsx3 saves as WAV via sapi5/nsss/espeak
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    engine.stop()

    if not os.path.exists(output_path):
        raise RuntimeError(f"File was not created at: {output_path}")

    return os.path.abspath(output_path)


# ─────────────────────────────────────────────
#  Online TTS  (gTTS / Google)
# ─────────────────────────────────────────────

LANGUAGE_MAP = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Hindi": "hi",
}


def get_supported_languages() -> dict[str, str]:
    """
    Return the subset of gTTS-supported languages we expose in the UI.

    Returns:
        Dict mapping display-name → ISO language code.
    """
    return LANGUAGE_MAP.copy()


def save_online_tts(text: str, output_path: str, language: str = "English",
                    slow: bool = False) -> str:
    """
    Convert *text* to speech using Google TTS and save as MP3.

    Args:
        text        : Text to synthesize.
        output_path : Destination .mp3 file path.
        language    : Display name key from LANGUAGE_MAP (default "English").
        slow        : If True, speak more slowly.

    Returns:
        Absolute path of the saved MP3 file.
    """
    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    lang_code = LANGUAGE_MAP.get(language, "en")

    tts = gTTS(text=text, lang=lang_code, slow=slow)
    tts.save(output_path)

    if not os.path.exists(output_path):
        raise RuntimeError(f"File was not created at: {output_path}")

    return os.path.abspath(output_path)


def generate_tts(text: str, output_path: str, engine_type: str = "online",
                 language: str = "English", rate: int = 150,
                 volume: float = 1.0, voice_index: int = 0,
                 slow: bool = False) -> str:
    """
    Unified TTS entry-point. Routes to online (gTTS) or offline (pyttsx3).

    Args:
        text        : Text to synthesize.
        output_path : Destination file path.
        engine_type : "online" or "offline".
        language    : Language name (used by online engine).
        rate        : Speech rate (used by offline engine).
        volume      : Volume (used by offline engine).
        voice_index : Voice index (used by offline engine).
        slow        : Slow mode (used by online engine).

    Returns:
        Absolute path of the saved audio file.
    """
    if engine_type == "online":
        return save_online_tts(text, output_path, language=language, slow=slow)
    elif engine_type == "offline":
        return save_offline_tts(text, output_path, rate=rate,
                                volume=volume, voice_index=voice_index)
    else:
        raise ValueError(f"Unknown engine_type: '{engine_type}'. Use 'online' or 'offline'.")
