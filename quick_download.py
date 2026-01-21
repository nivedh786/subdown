#!/usr/bin/env python3
"""快速下載指定 YouTube 影片的字幕或轉錄"""

import os
import sys
import yt_dlp
import whisper
import warnings

warnings.filterwarnings("ignore")

def remove_timeline_from_file(filename):
    """移除字幕檔案中的時間軸,只保留文字內容"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        clean_lines = []
        for line in lines:
            line = line.strip()
            if line.isdigit():
                continue
            if '-->' in line:
                continue
            if not line:
                continue
            if line.startswith('WEBVTT') or line.startswith('NOTE'):
                continue
            clean_lines.append(line)

        with open(filename, 'w', encoding='utf-8') as f:
            for line in clean_lines:
                f.write(line + '\n')

        print(f"✓ 已移除時間軸,純文字已保存至 {filename}")
        return True
    except Exception as e:
        print(f"✗ 移除時間軸時發生錯誤: {e}")
        return False

def check_and_download_subs(url, output_filename):
    """檢查並下載字幕（包含自動產生的字幕）"""
    print("正在檢查字幕...")
    ydl_opts_check = {
        'list_subtitles': True,
        'quiet': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_check) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get('subtitles', {})
            auto_captions = info.get('automatic_captions', {})

            # 優先使用手動字幕，其次使用自動字幕
            if subtitles:
                print(f"✓ 找到手動字幕: {list(subtitles.keys())}")
                sub_type = 'manual'
            elif auto_captions:
                print(f"✓ 找到自動產生的字幕: {list(auto_captions.keys())}")
                sub_type = 'auto'
            else:
                print("✗ 沒有找到任何字幕")
                return False

            print("正在下載字幕...")

            ydl_opts_down = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,  # 允許下載自動字幕
                'subtitleslangs': ['zh-Hant', 'zh-TW', 'zh', 'en'],  # 優先繁中、英文
                'outtmpl': 'temp_sub',
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts_down) as ydl_down:
                ydl_down.download([url])

            # 尋找下載的字幕檔案
            for file in os.listdir('.'):
                if file.startswith('temp_sub') and not file.endswith('.part'):
                    final_name = output_filename
                    if os.path.exists(final_name):
                        os.remove(final_name)
                    os.rename(file, final_name)
                    print(f"✓ 字幕已下載至 {final_name}")
                    return True

            print("✗ 無法找到下載的字幕檔案")
            return False

    except Exception as e:
        print(f"✗ 下載字幕時發生錯誤: {e}")
        return False

def download_audio_and_transcribe(url, output_filename):
    """下載音訊並使用 Whisper 轉錄"""
    print("正在下載音訊...")

    audio_base = "temp_audio"

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': audio_base,
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'geo_bypass': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"✗ 下載失敗: {e}")
        return False

    mp3_file = audio_base + ".mp3"

    if not os.path.exists(mp3_file):
        print("✗ 找不到音訊檔案")
        return False

    print("✓ 音訊下載成功")
    print("正在載入 Whisper 模型...")

    try:
        model = whisper.load_model("large")

        print("正在轉錄音訊（這可能需要較長時間）...")

        result = model.transcribe(
            mp3_file,
            language="en",
            condition_on_previous_text=False
        )

        print(f"正在保存轉錄結果至 {output_filename}...")

        with open(output_filename, "w", encoding="utf-8") as f:
            for segment in result['segments']:
                f.write(segment['text'].strip() + "\n")

        print("✓ 轉錄完成！")
        return True

    except Exception as e:
        print(f"✗ 轉錄失敗: {e}")
        return False
    finally:
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
            print("✓ 已清理暫存音訊檔案")

if __name__ == "__main__":
    # 直接在程式碼中設定 URL 和輸出檔名
    url = "https://www.youtube.com/watch?v=2P27Ef-LLuQ"
    output_filename = "samaltman2.txt"

    print(f"目標影片: {url}")
    print(f"輸出檔案: {output_filename}")
    print("-" * 60)

    # 步驟1: 嘗試下載字幕
    if check_and_download_subs(url, output_filename):
        remove_timeline_from_file(output_filename)
        print("-" * 60)
        print(f"✓ 完成！純文字已保存至 {output_filename}")
    else:
        # 步驟2: 如果沒有字幕，則轉錄音訊
        print("沒有可用的字幕，將改用 Whisper 轉錄音訊...")
        if download_audio_and_transcribe(url, output_filename):
            print("-" * 60)
            print(f"✓ 完成！轉錄已保存至 {output_filename}")
        else:
            print("-" * 60)
            print("✗ 處理失敗")
            sys.exit(1)
