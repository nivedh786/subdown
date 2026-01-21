# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

SubDown 是一個 YouTube 字幕下載與語音轉錄工具。核心功能：
1. 優先嘗試下載 YouTube 字幕（手動 + 自動產生）
2. 若無字幕或下載失敗，自動使用 OpenAI Whisper 進行語音轉文字
3. 自動移除時間軸，只保留純文字對話內容

## 常用指令

```bash
# 建立環境
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 命令列工具（推薦）
python download.py "https://www.youtube.com/watch?v=xxxxx"
python download.py "https://www.youtube.com/watch?v=xxxxx" -o output.txt
python download.py "https://www.youtube.com/watch?v=xxxxx" -m medium  # 較快的模型
python download.py "https://www.youtube.com/watch?v=xxxxx" --skip-subs  # 跳過字幕直接轉錄

# 互動式命令列
python main.py

# Streamlit 網頁介面
streamlit run app.py
```

## 程式架構

| 檔案 | 用途 |
|------|------|
| `download.py` | 主要命令列工具，支援完整參數（argparse） |
| `main.py` | 互動式 CLI，以 input() 取得使用者輸入 |
| `app.py` | Streamlit 網頁介面版本 |
| `quick_download.py` | 簡易範例腳本（URL 寫死在程式碼中） |

### 核心流程（三個版本共用邏輯）

1. `check_and_download_subs()` - 檢查並下載字幕
   - 優先手動字幕，其次自動字幕
   - 語言優先順序：zh-Hant → zh-TW → zh → en
2. `remove_timeline_from_file()` - 移除 VTT/SRT 時間軸
3. `download_audio_and_transcribe()` - 下載音訊後使用 Whisper 轉錄

### 技術細節

- 使用 yt-dlp 處理 YouTube 下載
- Whisper 模型預設使用 `large`，可透過 `-m` 切換
- 暫存檔案：`temp_audio.mp3`、`temp_sub.*`（處理後會清理）

## 語言設定

- 文件與註解使用繁體中文
- 程式碼本體維持英文
