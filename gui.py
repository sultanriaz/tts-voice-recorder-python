"""
gui.py
Tkinter desktop GUI for the TTS & Recording system.
Provides text input, TTS generation, voice recording, playback, and file saving.
"""

import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tts_module import (
    generate_tts,
    get_available_voices,
    get_supported_languages,
)
from recorder_module import AudioRecorder, play_audio_async


# ─────────────────────────────────────────────
#  Colour palette & fonts
# ─────────────────────────────────────────────

BG_DARK     = "#1E1E2E"
BG_PANEL    = "#2A2A3E"
BG_ENTRY    = "#313145"
ACCENT_BLUE = "#7B9FFF"
ACCENT_TEAL = "#4FC3A1"
ACCENT_ROSE = "#FF6B8A"
TEXT_MAIN   = "#E0E0F0"
TEXT_SUB    = "#9090B0"
FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_LABEL  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 10, "bold")
FONT_MONO   = ("Consolas", 10)

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TTS_TEMP    = os.path.join(OUTPUT_DIR, "tts_output.mp3")
REC_TEMP    = os.path.join(OUTPUT_DIR, "recording.wav")


# ─────────────────────────────────────────────
#  Main Application Window
# ─────────────────────────────────────────────

class TTSApp(tk.Tk):
    """Root window for the TTS & Recorder desktop application."""

    def __init__(self):
        super().__init__()

        self.title("🎙️ TTS & Voice Recorder")
        self.geometry("820x700")
        self.resizable(True, True)
        self.configure(bg=BG_DARK)
        self.minsize(700, 580)

        # State
        self._recorder       = AudioRecorder()
        self._tts_file: str  = ""
        self._rec_file: str  = ""

        self._build_ui()
        self._refresh_voices()

    # ─── UI Construction ──────────────────────

    def _build_ui(self):
        # ── Header ──────────────────────────────
        hdr = tk.Frame(self, bg=ACCENT_BLUE, height=4)
        hdr.pack(fill="x")

        title_bar = tk.Frame(self, bg=BG_DARK, pady=12)
        title_bar.pack(fill="x", padx=20)
        tk.Label(title_bar, text="🎙️  TTS & Voice Recorder",
                 font=FONT_TITLE, bg=BG_DARK, fg=TEXT_MAIN).pack(side="left")
        tk.Label(title_bar, text="Offline · Online · Urdu Support",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_SUB).pack(side="left", padx=12, pady=4)

        # ── Notebook tabs ────────────────────────
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",         background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",     background=BG_PANEL, foreground=TEXT_SUB,
                        font=FONT_BTN, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", "#FFFFFF")])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self._tts_tab = tk.Frame(nb, bg=BG_DARK)
        self._rec_tab = tk.Frame(nb, bg=BG_DARK)
        nb.add(self._tts_tab, text="  📢  Text-to-Speech  ")
        nb.add(self._rec_tab, text="  🎤  Voice Recorder  ")

        self._build_tts_tab()
        self._build_rec_tab()

        # ── Status bar ───────────────────────────
        self._status_var = tk.StringVar(value="Ready.")
        status_bar = tk.Frame(self, bg=BG_PANEL, height=28)
        status_bar.pack(fill="x", side="bottom")
        self._status_lbl = tk.Label(status_bar, textvariable=self._status_var,
                                    font=("Segoe UI", 9), bg=BG_PANEL, fg=TEXT_SUB,
                                    anchor="w", padx=10)
        self._status_lbl.pack(fill="x", side="left", expand=True)

    # ── TTS Tab ──────────────────────────────────

    def _build_tts_tab(self):
        p = self._tts_tab
        self._section(p, "Enter Text").pack(fill="x", padx=20, pady=(16, 4))

        # Text input
        txt_frame = tk.Frame(p, bg=BG_PANEL, bd=0, pady=2)
        txt_frame.pack(fill="both", padx=20, pady=(0, 12), expand=True)

        self._text_input = tk.Text(
            txt_frame, height=8, wrap="word",
            font=FONT_MONO, bg=BG_ENTRY, fg=TEXT_MAIN,
            insertbackground=ACCENT_TEAL, relief="flat",
            padx=10, pady=8, bd=0,
        )
        self._text_input.pack(fill="both", expand=True, padx=2, pady=2)
        self._text_input.insert("end",
            "Hello! Welcome to the TTS system.\n\n"
            "آپ یہاں اردو متن بھی لکھ سکتے ہیں۔")

        # Options row
        opts = tk.Frame(p, bg=BG_DARK)
        opts.pack(fill="x", padx=20, pady=(0, 12))

        # Engine
        self._lbl_opt(opts, "Engine:").grid(row=0, column=0, sticky="w", padx=(0, 4))
        self._engine_var = tk.StringVar(value="online")
        for i, (txt, val) in enumerate([("🌐 Online (Google)", "online"),
                                         ("💻 Offline (pyttsx3)", "offline")]):
            rb = tk.Radiobutton(opts, text=txt, variable=self._engine_var, value=val,
                                font=FONT_LABEL, bg=BG_DARK, fg=TEXT_MAIN,
                                selectcolor=BG_PANEL, activebackground=BG_DARK,
                                activeforeground=TEXT_MAIN,
                                command=self._on_engine_change)
            rb.grid(row=0, column=i+1, padx=6)

        # Language (online)
        self._lbl_opt(opts, "Language:").grid(row=0, column=4, sticky="w", padx=(16, 4))
        self._lang_var    = tk.StringVar(value="English")
        self._lang_combo  = ttk.Combobox(opts, textvariable=self._lang_var,
                                         values=list(get_supported_languages().keys()),
                                         width=14, state="readonly")
        self._lang_combo.grid(row=0, column=5, padx=4)

        # Slow speech (online)
        self._slow_var = tk.BooleanVar(value=False)
        tk.Checkbutton(opts, text="Slow", variable=self._slow_var,
                       font=FONT_LABEL, bg=BG_DARK, fg=TEXT_MAIN,
                       selectcolor=BG_PANEL, activebackground=BG_DARK,
                       activeforeground=TEXT_MAIN).grid(row=0, column=6, padx=8)

        # Voice (offline)
        self._voice_frame = tk.Frame(p, bg=BG_DARK)
        self._voice_frame.pack(fill="x", padx=20, pady=(0, 8))

        self._lbl_opt(self._voice_frame, "Voice:").pack(side="left", padx=(0, 6))
        self._voice_var   = tk.StringVar()
        self._voice_combo = ttk.Combobox(self._voice_frame, textvariable=self._voice_var,
                                         width=32, state="readonly")
        self._voice_combo.pack(side="left")

        self._lbl_opt(self._voice_frame, "Speed:").pack(side="left", padx=(16, 6))
        self._rate_var = tk.IntVar(value=150)
        tk.Scale(self._voice_frame, from_=50, to=300, orient="horizontal",
                 variable=self._rate_var, length=120,
                 bg=BG_DARK, fg=TEXT_MAIN, troughcolor=BG_PANEL,
                 highlightthickness=0, bd=0).pack(side="left")
        self._rate_lbl = tk.Label(self._voice_frame, textvariable=self._rate_var,
                                  font=FONT_LABEL, bg=BG_DARK, fg=TEXT_SUB, width=4)
        self._rate_lbl.pack(side="left")

        self._lbl_opt(self._voice_frame, "Vol:").pack(side="left", padx=(16, 4))
        self._vol_var = tk.DoubleVar(value=1.0)
        tk.Scale(self._voice_frame, from_=0.0, to=1.0, resolution=0.1,
                 orient="horizontal", variable=self._vol_var, length=80,
                 bg=BG_DARK, fg=TEXT_MAIN, troughcolor=BG_PANEL,
                 highlightthickness=0, bd=0).pack(side="left")

        self._voice_frame.pack_forget()   # Hidden until offline selected

        # Buttons
        btn_row = tk.Frame(p, bg=BG_DARK)
        btn_row.pack(fill="x", padx=20, pady=8)

        self._tts_btn      = self._btn(btn_row, "▶  Generate TTS",   ACCENT_BLUE,
                                       self._generate_tts)
        self._play_tts_btn = self._btn(btn_row, "🔊  Play",          ACCENT_TEAL,
                                       self._play_tts, state="disabled")
        self._save_tts_btn = self._btn(btn_row, "💾  Save Audio",    "#9B7FFF",
                                       self._save_tts, state="disabled")
        self._clear_btn    = self._btn(btn_row, "🗑  Clear",         ACCENT_ROSE,
                                       self._clear_tts)

        for b in (self._tts_btn, self._play_tts_btn,
                  self._save_tts_btn, self._clear_btn):
            b.pack(side="left", padx=4)

        # Progress bar
        self._tts_progress = ttk.Progressbar(p, mode="indeterminate", length=400)
        self._tts_progress.pack(pady=(4, 0))

    # ── Recorder Tab ─────────────────────────────

    def _build_rec_tab(self):
        p = self._rec_tab

        self._section(p, "Voice Recorder").pack(fill="x", padx=20, pady=(16, 4))

        # Visual indicator
        ind_frame = tk.Frame(p, bg=BG_DARK)
        ind_frame.pack(pady=20)

        self._rec_canvas = tk.Canvas(ind_frame, width=120, height=120,
                                     bg=BG_DARK, highlightthickness=0)
        self._rec_canvas.pack()
        self._draw_mic_indicator(active=False)

        self._rec_timer_var = tk.StringVar(value="00:00")
        tk.Label(ind_frame, textvariable=self._rec_timer_var,
                 font=("Segoe UI", 24, "bold"), bg=BG_DARK, fg=TEXT_MAIN).pack(pady=8)

        # Buttons
        btn_row = tk.Frame(p, bg=BG_DARK)
        btn_row.pack(pady=8)

        self._start_rec_btn = self._btn(btn_row, "⏺  Start Recording", ACCENT_ROSE,
                                        self._start_recording)
        self._stop_rec_btn  = self._btn(btn_row, "⏹  Stop",            "#666688",
                                        self._stop_recording, state="disabled")
        self._play_rec_btn  = self._btn(btn_row, "🔊  Play Back",       ACCENT_TEAL,
                                        self._play_recording, state="disabled")
        self._save_rec_btn  = self._btn(btn_row, "💾  Save Recording",  "#9B7FFF",
                                        self._save_recording, state="disabled")

        for b in (self._start_rec_btn, self._stop_rec_btn,
                  self._play_rec_btn, self._save_rec_btn):
            b.pack(side="left", padx=5)

        # Info panel
        info = tk.Frame(p, bg=BG_PANEL, pady=10, padx=16)
        info.pack(fill="x", padx=20, pady=20)
        lines = [
            ("Format",    "WAV · 44 100 Hz · 16-bit · Mono"),
            ("Max size",  "Limited only by disk space"),
            ("Playback",  "Via pygame (MP3+WAV) or pyaudio (WAV)"),
        ]
        for row, (k, v) in enumerate(lines):
            tk.Label(info, text=k + ":", font=("Segoe UI", 9, "bold"),
                     bg=BG_PANEL, fg=ACCENT_TEAL, anchor="w").grid(
                row=row, column=0, sticky="w", padx=(0, 12), pady=2)
            tk.Label(info, text=v, font=("Segoe UI", 9),
                     bg=BG_PANEL, fg=TEXT_SUB, anchor="w").grid(
                row=row, column=1, sticky="w")

    # ─── TTS Callbacks ────────────────────────

    def _generate_tts(self):
        text = self._text_input.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please enter some text first.")
            return

        self._set_status("Generating speech…")
        self._tts_btn.config(state="disabled")
        self._tts_progress.start(12)

        def _worker():
            try:
                engine = self._engine_var.get()
                voice_idx = 0

                if engine == "offline":
                    voices = get_available_voices()
                    sel    = self._voice_var.get()
                    for v in voices:
                        if v["name"] == sel:
                            voice_idx = v["index"]
                            break

                path = generate_tts(
                    text=text,
                    output_path=TTS_TEMP,
                    engine_type=engine,
                    language=self._lang_var.get(),
                    rate=self._rate_var.get(),
                    volume=self._vol_var.get(),
                    voice_index=voice_idx,
                    slow=self._slow_var.get(),
                )
                self._tts_file = path
                self.after(0, self._on_tts_success)
            except Exception as exc:
                self.after(0, lambda: self._on_tts_error(str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_tts_success(self):
        self._tts_progress.stop()
        self._tts_btn.config(state="normal")
        self._play_tts_btn.config(state="normal")
        self._save_tts_btn.config(state="normal")
        self._set_status(f"✅  TTS generated → {self._tts_file}", color=ACCENT_TEAL)

    def _on_tts_error(self, msg: str):
        self._tts_progress.stop()
        self._tts_btn.config(state="normal")
        self._set_status(f"❌  Error: {msg}", color=ACCENT_ROSE)
        messagebox.showerror("TTS Error", msg)

    def _play_tts(self):
        if not self._tts_file or not os.path.exists(self._tts_file):
            messagebox.showwarning("No Audio", "Generate TTS first.")
            return
        self._set_status("Playing audio…")
        play_audio_async(self._tts_file)

    def _save_tts(self):
        if not self._tts_file or not os.path.exists(self._tts_file):
            messagebox.showwarning("No Audio", "Generate TTS first.")
            return

        ext  = os.path.splitext(self._tts_file)[1]
        dest = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Audio files", f"*{ext}"), ("All files", "*.*")],
            title="Save TTS Audio",
        )
        if dest:
            shutil.copy2(self._tts_file, dest)
            self._set_status(f"💾  Saved → {dest}", color=ACCENT_TEAL)

    def _clear_tts(self):
        self._text_input.delete("1.0", "end")
        self._play_tts_btn.config(state="disabled")
        self._save_tts_btn.config(state="disabled")
        self._tts_file = ""
        self._set_status("Cleared.")

    # ─── Recorder Callbacks ───────────────────

    def _start_recording(self):
        try:
            self._recorder.start()
        except Exception as exc:
            messagebox.showerror("Microphone Error", str(exc))
            return

        self._start_rec_btn.config(state="disabled")
        self._stop_rec_btn.config(state="normal")
        self._play_rec_btn.config(state="disabled")
        self._save_rec_btn.config(state="disabled")
        self._draw_mic_indicator(active=True)
        self._set_status("🔴  Recording…", color=ACCENT_ROSE)
        self._rec_start_time = __import__("time").time()
        self._update_timer()

    def _stop_recording(self):
        try:
            path = self._recorder.stop(REC_TEMP)
            self._rec_file = path
        except Exception as exc:
            messagebox.showerror("Recording Error", str(exc))
            self._reset_recorder_ui()
            return

        self._reset_recorder_ui()
        self._play_rec_btn.config(state="normal")
        self._save_rec_btn.config(state="normal")
        self._set_status(f"✅  Recording saved → {self._rec_file}", color=ACCENT_TEAL)

    def _play_recording(self):
        if not self._rec_file or not os.path.exists(self._rec_file):
            messagebox.showwarning("No Recording", "Record audio first.")
            return
        self._set_status("Playing recording…")
        play_audio_async(self._rec_file)

    def _save_recording(self):
        if not self._rec_file or not os.path.exists(self._rec_file):
            messagebox.showwarning("No Recording", "Record audio first.")
            return

        dest = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            title="Save Recording",
        )
        if dest:
            shutil.copy2(self._rec_file, dest)
            self._set_status(f"💾  Saved → {dest}", color=ACCENT_TEAL)

    # ─── Timer & Indicator ────────────────────

    def _update_timer(self):
        if not self._recorder.is_recording:
            return
        elapsed = int(__import__("time").time() - self._rec_start_time)
        m, s    = divmod(elapsed, 60)
        self._rec_timer_var.set(f"{m:02d}:{s:02d}")
        self.after(1000, self._update_timer)

    def _draw_mic_indicator(self, active: bool):
        c = self._rec_canvas
        c.delete("all")
        colour = ACCENT_ROSE if active else "#555570"

        # Outer ring (pulsing when active)
        if active:
            c.create_oval(10, 10, 110, 110, outline=ACCENT_ROSE, width=3)

        # Mic body
        c.create_oval(40, 20, 80, 75, fill=colour, outline="")
        # Mic stand
        c.create_arc(25, 50, 95, 100, start=0, extent=-180,
                     style="arc", outline=colour, width=3)
        c.create_line(60, 100, 60, 115, fill=colour, width=3)
        c.create_line(48, 115, 72, 115, fill=colour, width=3)

    def _reset_recorder_ui(self):
        self._start_rec_btn.config(state="normal")
        self._stop_rec_btn.config(state="disabled")
        self._draw_mic_indicator(active=False)
        self._rec_timer_var.set("00:00")

    # ─── Engine change ────────────────────────

    def _on_engine_change(self):
        if self._engine_var.get() == "offline":
            self._voice_frame.pack(fill="x", padx=20, pady=(0, 8))
        else:
            self._voice_frame.pack_forget()

    def _refresh_voices(self):
        try:
            voices = get_available_voices()
            names  = [v["name"] for v in voices] or ["Default"]
        except Exception:
            names  = ["Default"]
        self._voice_combo["values"] = names
        if names:
            self._voice_var.set(names[0])

    # ─── Helpers ──────────────────────────────

    def _set_status(self, msg: str, color: str = TEXT_SUB):
        self._status_var.set(msg)
        self._status_lbl.config(fg=color)

    @staticmethod
    def _section(parent, title: str) -> tk.Label:
        lbl = tk.Label(parent, text=f"  {title}",
                       font=("Segoe UI", 11, "bold"),
                       bg=BG_PANEL, fg=ACCENT_BLUE,
                       anchor="w", pady=6, padx=10)
        return lbl

    @staticmethod
    def _lbl_opt(parent, text: str) -> tk.Label:
        return tk.Label(parent, text=text, font=FONT_LABEL,
                        bg=BG_DARK, fg=TEXT_SUB)

    @staticmethod
    def _btn(parent, text: str, colour: str,
             command, state: str = "normal") -> tk.Button:
        return tk.Button(
            parent, text=text, command=command,
            font=FONT_BTN, bg=colour, fg="#FFFFFF",
            activebackground=colour, activeforeground="#FFFFFF",
            relief="flat", bd=0, padx=14, pady=7,
            cursor="hand2", state=state,
        )


# ─────────────────────────────────────────────
#  Entry-point (used when running gui.py directly)
# ─────────────────────────────────────────────

def launch():
    app = TTSApp()
    app.mainloop()


if __name__ == "__main__":
    launch()
