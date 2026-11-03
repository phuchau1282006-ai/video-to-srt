Công cụ offline tạo phụ đề .srt từ video bằng Whisper

# Video to SRT — by PhucHau

🇻🇳 [Tiếng Việt](#-tiếng-việt) | 🇬🇧 [English](#-english)

---

## 🇻🇳 Tiếng Việt

Công cụ chạy **offline** trên máy tính: chọn một video, app sẽ nhận diện giọng nói và xuất ra file phụ đề **.srt** (chữ hiện theo mốc thời gian). File này chỉ chứa chữ và thời gian, không chứa hình hay tiếng của video, nên import thẳng vào **CapCut** được.

Dùng [faster-whisper](https://github.com/SYSTRAN/faster-whisper) để nhận diện giọng nói. Sau lần tải model đầu tiên, app chạy hoàn toàn không cần mạng.

### Tính năng
- Giao diện đơn giản, chọn video là chạy.
- Hỗ trợ tiếng Việt, English, 中文, 日本語, 한국어 hoặc tự nhận diện ngôn ngữ.
- Chọn model: `tiny`, `base`, `small`, `medium`, `large-v3` (càng lớn càng chính xác nhưng càng chậm).
- Tự chia phụ đề thành các dòng ngắn, dễ đọc (khoảng 42 ký tự hoặc 5 giây mỗi dòng).
- File `.srt` được lưu cạnh video, cùng tên.

### Cài đặt
1. Cài [Python](https://www.python.org/downloads/) 3.9 trở lên (khi cài, tick **Add Python to PATH**).
2. Tải repo này về, mở terminal trong thư mục đó và chạy:
   ```bash
   pip install -r requirements.txt
   ```

### Cách dùng
```bash
python app.py
```
1. Bấm **Chọn file** và chọn video (hoặc file âm thanh).
2. Chọn **Ngôn ngữ nói** và **Model**.
3. Bấm **Tạo phụ đề** và chờ thanh tiến trình chạy xong.
4. Lấy file `.srt` ở cạnh video (có nút mở thư mục).

> Lần chạy đầu tiên app sẽ tải model nên cần có mạng và hơi lâu.

### Import vào CapCut
Trong CapCut bản máy tính, vào **Chữ → Phụ đề → Nhập phụ đề** (Captions → Import captions), rồi chọn file `.srt`. Tên menu có thể hơi khác tùy phiên bản CapCut.

### Lỗi thường gặp
| Lỗi | Cách xử lý |
|---|---|
| `open() got an unexpected keyword argument 'metadata_errors'` | Thư viện `av` quá mới. Chạy: `pip install "av<16"` |
| `Library cublas64_12.dll is not found` | Máy chưa có CUDA. App này mặc định chạy bằng CPU (`device="cpu"`), hãy dùng bản `app.py` mới nhất. |
| Chạy chậm | Dùng model nhỏ hơn (`base`, `small`) hoặc video ngắn hơn. |
| Sai tên riêng / từ chuyên ngành | Đổi sang model lớn hơn, hoặc sửa lại trong CapCut. |

### Giấy phép
MIT License — © 2026 PhucHau. Xem file [LICENSE](LICENSE).

---

## 🇬🇧 English

An **offline** desktop tool: pick a video, and the app transcribes the speech into a timestamped **.srt** subtitle file. The file contains only text and timing (no video or audio), so you can import it straight into **CapCut**.

Speech recognition is powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper). After the model is downloaded the first time, the app works fully offline.

### Features
- Simple GUI: choose a video and go.
- Supports Vietnamese, English, Chinese, Japanese, Korean, or automatic language detection.
- Selectable model: `tiny`, `base`, `small`, `medium`, `large-v3` (larger = more accurate but slower).
- Automatically splits subtitles into short, readable lines (about 42 characters or 5 seconds each).
- The `.srt` file is saved next to the video with the same name.

### Installation
1. Install [Python](https://www.python.org/downloads/) 3.9 or newer (tick **Add Python to PATH** during setup).
2. Download this repo, open a terminal in its folder and run:
   ```bash
   pip install -r requirements.txt
   ```

### Usage
```bash
python app.py
```
1. Click **Chọn file** (choose file) and select a video or audio file.
2. Pick the **spoken language** and the **model**.
3. Click **Tạo phụ đề** (generate subtitles) and wait for the progress bar to finish.
4. Find the `.srt` file next to your video (there is a button to open the folder).

> The first run downloads the model, so an internet connection is required and it may take a while.

### Importing into CapCut
In CapCut Desktop, go to **Text → Captions → Import captions** and select the `.srt` file. Menu names may differ slightly between CapCut versions.

### Troubleshooting
| Error | Fix |
|---|---|
| `open() got an unexpected keyword argument 'metadata_errors'` | The `av` package is too new. Run: `pip install "av<16"` |
| `Library cublas64_12.dll is not found` | CUDA is not installed. This app runs on CPU by default (`device="cpu"`); use the latest `app.py`. |
| Slow processing | Use a smaller model (`base`, `small`) or a shorter video. |
| Wrong names / jargon | Use a larger model, or correct the text in CapCut. |

### License
MIT License — © 2026 PhucHau. See [LICENSE](LICENSE).
