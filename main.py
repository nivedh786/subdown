import os
import sys
import yt_dlp
import whisper
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def remove_timeline_from_file(filename):
    """
    移除字幕檔案中的時間軸,只保留文字內容。
    支援常見的字幕格式 (SRT, VTT 等)。
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        clean_lines = []
        for line in lines:
            line = line.strip()
            # 跳過序號行 (純數字)
            if line.isdigit():
                continue
            # 跳過時間軸行 (包含 --> 的行)
            if '-->' in line:
                continue
            # 跳過空行
            if not line:
                continue
            # 跳過 WEBVTT 標頭
            if line.startswith('WEBVTT') or line.startswith('NOTE'):
                continue
            # 保留實際的字幕文字
            clean_lines.append(line)

        # 寫回檔案
        with open(filename, 'w', encoding='utf-8') as f:
            for line in clean_lines:
                f.write(line + '\n')

        print(f"已移除時間軸,純文字已保存至 {filename}")
        return True
    except Exception as e:
        print(f"移除時間軸時發生錯誤: {e}")
        return False

def check_and_download_subs(url, output_filename):
    """
    Checks for subtitles. If present, downloads them.
    Returns True if subtitles were found and downloaded, False otherwise.
    """
    print("Checking for existing subtitles...")
    ydl_opts_check = {
        'list_subtitles': True,
        'quiet': True,
        'skip_download': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_check) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get('subtitles', {})
            
            if subtitles:
                print(f"Subtitles found: {list(subtitles.keys())}")
                print("Downloading subtitles...")
                
                ydl_opts_down = {
                    'skip_download': True,
                    'writesubtitles': True,
                    'subtitleslangs': ['en', 'all'],
                    'outtmpl': 'temp_sub',
                    'quiet': True,
                    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                }
                with yt_dlp.YoutubeDL(ydl_opts_down) as ydl_down:
                    ydl_down.download([url])
                
                for file in os.listdir('.'):
                    if file.startswith('temp_sub') and not file.endswith('.part'):
                        final_name = output_filename
                        if os.path.exists(final_name):
                            os.remove(final_name)
                        os.rename(file, final_name)
                        return True
                return False
            else:
                print("No manual subtitles found.")
                return False
    except Exception as e:
        print(f"Error checking subtitles: {e}")
        return False

def download_audio_and_transcribe(url, output_filename):
    """
    Downloads audio as MP3 and transcribes using Whisper Large.
    """
    print("Attempting to download audio...")
    
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
        # 使用 cookies 和 user-agent 來避免 403 錯誤
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        # 使用 android client 避免 SABR streaming 問題
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Download failed: {e}")
        return False

    mp3_file = audio_base + ".mp3"
    
    if not os.path.exists(mp3_file):
        print("Audio file not found after download attempt.")
        return False

    print("Audio downloaded successfully.")
    print("Loading Whisper 'large' model... (this may take time on first run)")
    
    try:
        model = whisper.load_model("large")
        
        print("Transcribing audio... (this may take a long time)")
        
        result = model.transcribe(
            mp3_file, 
            language="en", 
            condition_on_previous_text=False
        )
        
        print(f"Saving transcription to {output_filename}...")
        
        with open(output_filename, "w", encoding="utf-8") as f:
            for segment in result['segments']:
                f.write(segment['text'].strip() + "\n")
                
        print("Transcription complete!")
        return True
        
    except Exception as e:
        print(f"Transcription failed: {e}")
        return False
    finally:
        if os.path.exists(mp3_file):
            os.remove(mp3_file)

def main():
    url = input("請輸入網址：")
    output_filename = input("請輸入檔名 (例如: my_transcript.txt)：")
    
    if not output_filename.endswith(".txt"):
        output_filename += ".txt"
        
    if check_and_download_subs(url, output_filename):
        print(f"字幕已下載至 {output_filename}")
        # 自動移除時間軸
        remove_timeline_from_file(output_filename)
        print(f"處理完成: 純文字已保存至 {output_filename}")
    else:
        if download_audio_and_transcribe(url, output_filename):
            print(f"處理完成: 轉錄已保存至 {output_filename}")
        else:
            print("處理失敗")

if __name__ == "__main__":
    main()
