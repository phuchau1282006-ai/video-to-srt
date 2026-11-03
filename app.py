"""
PhucHau - Video -> Phụ đề SRT
Chạy offline trên máy (faster-whisper). File .srt chỉ chứa chữ + mốc thời gian,
import thẳng vào CapCut.
(c) 2026 PhucHau
"""
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from faster_whisper import WhisperModel

APP_AUTHOR = "PhucHau"
APP_NAME = "Video → Phụ đề SRT"

MODELS = ["tiny", "base", "small", "medium", "large-v3"]
LANGS = {
    "Tự nhận diện": None,
    "Tiếng Việt": "vi",
    "English": "en",
    "中文": "zh",
    "日本語": "ja",
    "한국어": "ko",
}

MAX_CHARS = 42      # số ký tự tối đa mỗi dòng phụ đề
MAX_SECONDS = 5.0   # thời lượng tối đa mỗi dòng phụ đề

# Bảng màu
BG = "#f4f5fb"
CARD = "#ffffff"
PRIMARY = "#6c4cf1"
PRIMARY_DARK = "#5638d6"
TEXT = "#23263a"
MUTED = "#80849a"
HEADER_FROM = "#6c4cf1"
SUCCESS = "#1f9d62"
ERROR = "#d64545"


def fmt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_cues(segments):
    """Chia nhỏ theo từng từ để mỗi dòng phụ đề ngắn, dễ đọc."""
    cues = []
    cur_words, cur_start, cur_end = [], None, None

    def flush():
        nonlocal cur_words, cur_start, cur_end
        text = "".join(cur_words).strip()
        if text:
            cues.append((cur_start, cur_end, text))
        cur_words, cur_start, cur_end = [], None, None

    for seg in segments:
        words = seg.words or []
        if not words:
            flush()
            cues.append((seg.start, seg.end, seg.text.strip()))
            continue
        for w in words:
            if cur_start is None:
                cur_start = w.start
            cur_words.append(w.word)
            cur_end = w.end
            text_len = len("".join(cur_words).strip())
            ends_sentence = w.word.strip().endswith((".", "?", "!", "。", "？", "！"))
            if (
                text_len >= MAX_CHARS
                or (cur_end - cur_start) >= MAX_SECONDS
                or (ends_sentence and text_len > 15)
            ):
                flush()
        flush()
    return cues


def transcribe_to_srt(video_path, model_name, lang, progress_cb):
    progress_cb("Đang tải model (lần đầu sẽ hơi lâu)...", None)
    model = WhisperModel(model_name, device="cpu", compute_type="int8")

    progress_cb("Đang nhận diện giọng nói...", 0)
    segments, info = model.transcribe(
        video_path,
        language=lang,
        vad_filter=True,
        word_timestamps=True,
    )

    seg_list = []
    total = info.duration or 1
    for seg in segments:
        seg_list.append(seg)
        pct = min(99, int(seg.end / total * 100))
        progress_cb(f"Đang xử lý... {pct}%", pct)

    cues = build_cues(seg_list)
    out_path = os.path.splitext(video_path)[0] + ".srt"
    with open(out_path, "w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(cues, 1):
            f.write(f"{i}\n{fmt_time(start)} --> {fmt_time(end)}\n{text}\n\n")
    return out_path, info.language


def open_folder(path):
    folder = os.path.dirname(os.path.abspath(path))
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", "/select,", os.path.abspath(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    except Exception:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} • {APP_AUTHOR}")
        self.geometry("620x520")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.video_path = tk.StringVar()
        self.model_name = tk.StringVar(value="small")
        self.lang_name = tk.StringVar(value="Tiếng Việt")
        self.status = tk.StringVar(value="Chọn video để bắt đầu.")
        self.out_path = None

        self._setup_style()
        self._build_header()
        self._build_body()
        self._build_footer()

    # ---------- style ----------
    def _setup_style(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("TFrame", background=BG)
        st.configure("Card.TFrame", background=CARD)
        st.configure("Card.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10))
        st.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        st.configure("TCombobox", padding=6, font=("Segoe UI", 10))
        st.configure("TEntry", padding=6)
        st.configure(
            "Primary.TButton",
            background=PRIMARY, foreground="white",
            font=("Segoe UI", 11, "bold"), padding=(18, 10), borderwidth=0,
        )
        st.map("Primary.TButton",
               background=[("active", PRIMARY_DARK), ("disabled", "#b9aef5")],
               foreground=[("disabled", "#ffffff")])
        st.configure(
            "Ghost.TButton",
            background="#ece9fd", foreground=PRIMARY,
            font=("Segoe UI", 10, "bold"), padding=(12, 6), borderwidth=0,
        )
        st.map("Ghost.TButton", background=[("active", "#ddd7fb")])
        st.configure(
            "Bar.Horizontal.TProgressbar",
            troughcolor="#e6e8f2", background=PRIMARY, bordercolor=CARD,
            lightcolor=PRIMARY, darkcolor=PRIMARY, thickness=10,
        )

    # ---------- header với logo ----------
    def _build_header(self):
        header = tk.Canvas(self, width=620, height=110, highlightthickness=0, bg=BG)
        header.pack(fill="x")

        # nền gradient ngang tím -> xanh
        c1 = (108, 76, 241)
        c2 = (60, 140, 250)
        for x in range(620):
            t = x / 619
            col = "#%02x%02x%02x" % tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
            header.create_line(x, 0, x, 110, fill=col)

        # logo: ô vuông bo tròn + "PH"
        self._rounded_rect(header, 24, 22, 90, 88, 16, fill="white")
        header.create_text(57, 55, text="PH", fill=PRIMARY, font=("Segoe UI", 24, "bold"))

        header.create_text(108, 42, anchor="w", text=APP_AUTHOR,
                           fill="white", font=("Segoe UI", 22, "bold"))
        header.create_text(110, 74, anchor="w", text="Video  →  Phụ đề SRT cho CapCut",
                           fill="#e6e1ff", font=("Segoe UI", 11))

    @staticmethod
    def _rounded_rect(cv, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return cv.create_polygon(pts, smooth=True, **kw)

    # ---------- phần thân ----------
    def _build_body(self):
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        card = ttk.Frame(wrap, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Video / Âm thanh", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 4), columnspan=3)
        ttk.Entry(card, textvariable=self.video_path).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8))
        ttk.Button(card, text="Chọn file", style="Ghost.TButton", command=self.pick).grid(
            row=1, column=2)

        ttk.Label(card, text="Ngôn ngữ nói", style="Card.TLabel").grid(
            row=2, column=0, sticky="w", pady=(16, 4))
        ttk.Label(card, text="Model", style="Card.TLabel").grid(
            row=2, column=1, sticky="w", pady=(16, 4), padx=(12, 0))
        ttk.Combobox(card, textvariable=self.lang_name, values=list(LANGS),
                     state="readonly").grid(row=3, column=0, sticky="ew")
        ttk.Combobox(card, textvariable=self.model_name, values=MODELS,
                     state="readonly").grid(row=3, column=1, sticky="ew", padx=(12, 0))

        ttk.Label(card, text="small = cân bằng • medium / large-v3 chính xác hơn nhưng chậm hơn",
                  style="Muted.TLabel").grid(row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))

        self.btn = ttk.Button(card, text="▶  Tạo phụ đề", style="Primary.TButton", command=self.start)
        self.btn.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(20, 12))

        self.bar = ttk.Progressbar(card, style="Bar.Horizontal.TProgressbar",
                                   mode="determinate", maximum=100)
        self.bar.grid(row=6, column=0, columnspan=3, sticky="ew")

        self.status_lbl = tk.Label(card, textvariable=self.status, bg=CARD, fg=MUTED,
                                   font=("Segoe UI", 10), wraplength=520, justify="left", anchor="w")
        self.status_lbl.grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.open_btn = ttk.Button(card, text="📂  Mở thư mục chứa file .srt",
                                   style="Ghost.TButton", command=self.show_result)
        self.open_btn.grid(row=8, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.open_btn.grid_remove()

    def _build_footer(self):
        tk.Label(self, text=f"© 2026 {APP_AUTHOR} • All rights reserved",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(pady=(0, 10))

    # ---------- hành vi ----------
    def pick(self):
        p = filedialog.askopenfilename(
            filetypes=[("Video/Audio", "*.mp4 *.mov *.mkv *.avi *.webm *.mp3 *.wav *.m4a"),
                       ("Tất cả", "*.*")]
        )
        if p:
            self.video_path.set(p)

    def set_status(self, msg, pct=None, color=MUTED):
        def apply():
            self.status.set(msg)
            self.status_lbl.config(fg=color)
            if pct is not None:
                self.bar.config(mode="determinate")
                self.bar["value"] = pct
        self.after(0, apply)

    def show_result(self):
        if self.out_path:
            open_folder(self.out_path)

    def start(self):
        path = self.video_path.get().strip()
        if not os.path.isfile(path):
            messagebox.showwarning("Thiếu video", "Hãy chọn một file video hợp lệ.")
            return
        self.btn.state(["disabled"])
        self.open_btn.grid_remove()
        self.bar["value"] = 0
        lang = LANGS[self.lang_name.get()]
        threading.Thread(target=self.work, args=(path, self.model_name.get(), lang),
                         daemon=True).start()

    def work(self, path, model, lang):
        try:
            out, detected = transcribe_to_srt(
                path, model, lang, lambda m, p=None: self.set_status(m, p))
            self.out_path = out
            self.set_status(f"Xong! (ngôn ngữ: {detected})\nĐã lưu: {out}", 100, SUCCESS)
            self.after(0, self.open_btn.grid)
        except Exception as e:
            self.set_status(f"Lỗi: {e}", 0, ERROR)
        finally:
            self.after(0, lambda: self.btn.state(["!disabled"]))


if __name__ == "__main__":
    App().mainloop()
