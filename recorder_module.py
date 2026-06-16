

import os
import wave
import threading
import time
import pyaudio



CHUNK       = 1024          # Samples per buffer frame
FORMAT      = pyaudio.paInt16
CHANNELS    = 1             # Mono recording
RATE        = 44100         # Sample rate (Hz)

class AudioRecorder:


    def __init__(self, channels: int = CHANNELS, rate: int = RATE,
                 chunk: int = CHUNK):
        self.channels  = channels
        self.rate      = rate
        self.chunk     = chunk

        self._frames: list[bytes] = []
        self._is_recording        = False
        self._thread: threading.Thread | None = None
        self._pyaudio: pyaudio.PyAudio | None = None
        self._stream = None

    # ── public API ──────────────────────────

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start(self) -> None:
        """Start recording audio in a background thread."""
        if self._is_recording:
            raise RuntimeError("Recording is already in progress.")

        self._frames         = []
        self._is_recording   = True
        self._pyaudio        = pyaudio.PyAudio()

        self._stream = self._pyaudio.open(
            format=FORMAT,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self, output_path: str) -> str:
    
        if not self._is_recording:
            raise RuntimeError("No recording is in progress.")

        self._is_recording = False

        # Wait for the recording thread to finish
        if self._thread:
            self._thread.join(timeout=5)

        # Tear down PyAudio resources
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pyaudio:
            self._pyaudio.terminate()

        if not self._frames:
            raise RuntimeError("No audio data was captured.")

        return self._save_wav(output_path)

    # ── internal helpers ────────────────────

    def _record_loop(self) -> None:
        """Background thread that continuously reads audio frames."""
        while self._is_recording:
            try:
                data = self._stream.read(self.chunk, exception_on_overflow=False)
                self._frames.append(data)
            except Exception:
                break

    def _save_wav(self, output_path: str) -> str:
        """Write collected frames to a WAV file."""
        pa = pyaudio.PyAudio()
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(pa.get_sample_size(FORMAT))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(self._frames))
        pa.terminate()
        return os.path.abspath(output_path)


# ─────────────────────────────────────────────
#  Synchronous (blocking) helper
# ─────────────────────────────────────────────

def record_audio(output_path: str, duration: float) -> str:
    if duration <= 0:
        raise ValueError("Duration must be a positive number.")

    recorder = AudioRecorder()
    recorder.start()
    time.sleep(duration)
    return recorder.stop(output_path)


# ─────────────────────────────────────────────
#  Playback
# ─────────────────────────────────────────────

def play_audio(file_path: str) -> None:

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    # ── pygame playback (MP3 + WAV) ──────────
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Block until playback finishes
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        return
    except ImportError:
        pass  # pygame not installed; fall through to pyaudio WAV path
    except Exception as exc:
        raise RuntimeError(f"pygame playback failed: {exc}") from exc

    # ── pyaudio fallback (WAV only) ──────────
    if ext != ".wav":
        raise RuntimeError(
            
        )

    pa = pyaudio.PyAudio()
    with wave.open(file_path, "rb") as wf:
        stream = pa.open(
            format=pa.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )
        data = wf.readframes(CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
    pa.terminate()


def play_audio_async(file_path: str) -> threading.Thread:
  
    t = threading.Thread(target=play_audio, args=(file_path,), daemon=True)
    t.start()
    return t


# ─────────────────────────────────────────────
#  Utility
# ─────────────────────────────────────────────

def get_wav_duration(file_path: str) -> float:
 
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with wave.open(file_path, "rb") as wf:
        frames = wf.getnframes()
        rate   = wf.getframerate()
        return frames / float(rate)


def list_microphones() -> list[dict]:
    
    pa      = pyaudio.PyAudio()
    devices = []
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            devices.append({"index": i, "name": info["name"]})
    pa.terminate()
    return devices
