#!/usr/bin/env python3
"""YouTube 字幕下載 / 語音轉錄工具
支援命令列參數，可快速處理任何 YouTube 影片
"""

import os
import sys
import argparse
import yt_dlp
import whisper
import warnings

warnings.filterwarnings("ignore")

def remove_timeline_from_file(filename):
    """移除字幕檔案中的時間軸，只保留文字內容"""
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

        print(f"✓ 已移除時間軸，純文字已保存至 {filename}")
        return True
    except Exception as e:
        print(f"✗ 移除時間軸時發生錯誤: {e}")
        return False

def check_and_download_subs(url, output_filename, langs=['zh-Hant', 'zh-TW', 'zh', 'en']):
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

            if subtitles:
                print(f"✓ 找到手動字幕: {list(subtitles.keys())}")
                sub_type = 'manual'
            elif auto_captions:
                print(f"✓ 找到自動產生的字幕: {list(auto_captions.keys())}")
                sub_type = 'auto'
            else:
                print("✗ 沒有找到任何字幕")
                return False

            print(f"正在下載字幕（優先語言: {', '.join(langs)}）...")

            ydl_opts_down = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': langs,
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

def download_audio_and_transcribe(url, output_filename, model_size='large', language=None):
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
    print(f"正在載入 Whisper '{model_size}' 模型...")

    try:
        model = whisper.load_model(model_size)

        print("正在轉錄音訊（這可能需要較長時間）...")

        # 自動偵測語言或使用指定語言
        transcribe_opts = {
            'condition_on_previous_text': False
        }
        if language:
            transcribe_opts['language'] = language

        result = model.transcribe(mp3_file, **transcribe_opts)

        print(f"正在保存轉錄結果至 {output_filename}...")

        with open(output_filename, "w", encoding="utf-8") as f:
            for segment in result['segments']:
                f.write(segment['text'].strip() + "\n")

        detected_lang = result.get('language', 'unknown')
        print(f"✓ 轉錄完成！（偵測到的語言: {detected_lang}）")
        return True

    except Exception as e:
        print(f"✗ 轉錄失敗: {e}")
        return False
    finally:
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
            print("✓ 已清理暫存音訊檔案")

def main():
    parser = argparse.ArgumentParser(
        description='YouTube 字幕下載 / 語音轉錄工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s https://www.youtube.com/watch?v=xxxxx
  %(prog)s https://www.youtube.com/watch?v=xxxxx -o output.txt
  %(prog)s https://www.youtube.com/watch?v=xxxxx -l en -m medium
  %(prog)s https://www.youtube.com/watch?v=xxxxx --skip-subs
        """
    )

    parser.add_argument('url', help='YouTube 影片網址')
    parser.add_argument('-o', '--output', help='輸出檔案名稱（預設: transcription.txt）', default='transcription.txt')
    parser.add_argument('-l', '--lang', help='Whisper 轉錄語言（預設: 自動偵測）', default=None)
    parser.add_argument('-m', '--model', help='Whisper 模型大小（tiny/base/small/medium/large）（預設: large）',
                        choices=['tiny', 'base', 'small', 'medium', 'large'], default='large')
    parser.add_argument('--skip-subs', help='跳過字幕下載，直接使用 Whisper 轉錄', action='store_true')
    parser.add_argument('--sub-langs', help='字幕語言優先順序（預設: zh-Hant,zh-TW,zh,en）', default='zh-Hant,zh-TW,zh,en')

    args = parser.parse_args()

    # 確保檔名有 .txt 副檔名
    if not args.output.endswith('.txt'):
        args.output += '.txt'

    # 解析字幕語言清單
    sub_langs = [lang.strip() for lang in args.sub_langs.split(',')]

    print("=" * 60)
    print(f"YouTube 字幕下載工具")
    print("=" * 60)
    print(f"影片網址: {args.url}")
    print(f"輸出檔案: {args.output}")
    print(f"Whisper 模型: {args.model}")
    if args.lang:
        print(f"轉錄語言: {args.lang}")
    print("=" * 60)

    success = False

    # 步驟1: 嘗試下載字幕（除非使用者要求跳過）
    if not args.skip_subs:
        if check_and_download_subs(args.url, args.output, sub_langs):
            remove_timeline_from_file(args.output)
            print("-" * 60)
            print(f"✓ 完成！純文字已保存至 {args.output}")
            success = True

    # 步驟2: 如果沒有字幕或使用者要求跳過，則轉錄音訊
    if not success:
        if args.skip_subs:
            print("已跳過字幕下載，將使用 Whisper 轉錄音訊...")
        else:
            print("沒有可用的字幕，將改用 Whisper 轉錄音訊...")

        if download_audio_and_transcribe(args.url, args.output, args.model, args.lang):
            print("-" * 60)
            print(f"✓ 完成！轉錄已保存至 {args.output}")
            success = True

    if not success:
        print("-" * 60)
        print("✗ 處理失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
