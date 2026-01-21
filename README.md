# SubDown - YouTube 字幕下載與轉錄工具

自動下載 YouTube 字幕或使用 Whisper AI 進行語音轉文字。

## 功能特色

- ✅ **智慧備援機制**：優先嘗試下載現有字幕，失敗時自動使用 Whisper AI 轉錄
- ✅ **自動字幕支援**：可下載 YouTube 自動產生的字幕
- ✅ **多語言支援**：優先繁體中文，支援自訂語言順序
- ✅ **純文字輸出**：自動移除時間軸，只保留對話內容
- ✅ **HTTP 429 自動處理**：遇到 API 限制時自動切換到 Whisper 轉錄
- ✅ **無需訂閱**：即使沒有 YouTube Premium 也能取得完整轉錄

## 安裝

確保已安裝 Python 3.8+ 和 FFmpeg：

```bash
# 安裝 FFmpeg（Ubuntu/Debian）
sudo apt install ffmpeg

# 安裝 Python 套件
uv pip install -r requirements.txt
```

## 使用方式

### 1. 命令列工具（推薦）

基本使用：
```bash
python download.py "https://www.youtube.com/watch?v=2P27Ef-LLuQ"
```

指定輸出檔名：
```bash
python download.py "https://www.youtube.com/watch?v=2P27Ef-LLuQ" -o samaltman.txt
```

強制使用 Whisper 轉錄（跳過字幕下載）：
```bash
python download.py "https://www.youtube.com/watch?v=2P27Ef-LLuQ" --skip-subs
```

使用較小的模型加快速度：
```bash
python download.py "https://www.youtube.com/watch?v=2P27Ef-LLuQ" -m medium
```

指定轉錄語言：
```bash
python download.py "https://www.youtube.com/watch?v=2P27Ef-LLuQ" -l en
```

自訂字幕語言優先順序：
```bash
python download.py "https://www.youtube.com/watch?v=2P27Ef-LLuQ" --sub-langs "en,ja,ko"
```

### 2. 互動式命令列

```bash
python main.py
```

會詢問您輸入網址和檔名。

### 3. Streamlit 網頁介面

```bash
streamlit run app.py
```

在瀏覽器中開啟 http://localhost:8501 使用圖形介面。

## 工作流程

```
開始
  ↓
檢查是否有字幕（手動 + 自動）
  ↓
  有字幕 → 下載字幕 → 移除時間軸 → 完成
  ↓
  沒有字幕或下載失敗（HTTP 429）
  ↓
下載音訊（MP3）
  ↓
使用 Whisper AI 轉錄
  ↓
保存純文字 → 完成
```

## Whisper 模型選擇

| 模型 | 速度 | 準確度 | 記憶體 | 適用場景 |
|------|------|--------|--------|----------|
| tiny | 超快 | 較低 | ~1 GB | 快速預覽 |
| base | 快 | 中等 | ~1 GB | 一般用途 |
| small | 中等 | 良好 | ~2 GB | 平衡選擇 |
| medium | 慢 | 很好 | ~5 GB | 高品質需求 |
| large | 很慢 | 最佳 | ~10 GB | 專業品質（預設）|

## 常見問題

### Q: 遇到 HTTP 429 錯誤怎麼辦？

這是 YouTube 的請求頻率限制。程式會自動切換到 Whisper 轉錄，無需擔心。

### Q: 沒有訂閱可以下載字幕嗎？

可以！本工具不需要 YouTube Premium。如果無法下載字幕，會自動使用 Whisper AI 轉錄音訊。

### Q: 轉錄需要多久時間？

取決於影片長度和選擇的模型：
- 使用 `large` 模型：約為影片長度的 20-50%
- 使用 `medium` 模型：約為影片長度的 10-30%
- 首次執行需要下載模型（一次性）

### Q: 支援哪些語言？

Whisper 支援 99 種語言，包括：
- 中文（繁體/簡體）
- 英文
- 日文
- 韓文
- 西班牙文
- 法文
- 德文
- 等等...

可使用 `-l` 參數指定語言，或留空讓 Whisper 自動偵測。

## 檔案說明

- `download.py` - 功能完整的命令列工具（推薦）
- `main.py` - 互動式命令列版本
- `app.py` - Streamlit 網頁介面
- `quick_download.py` - 簡單的單一用途範例

## 授權

MIT License

## 技術棧

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 下載器
- [OpenAI Whisper](https://github.com/openai/whisper) - 語音轉文字 AI
- [Streamlit](https://streamlit.io/) - 網頁介面（可選）
