import os
import subprocess
from moviepy import VideoFileClip

def extract_audio(video_path, output_audio_path):
    try:
        
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vn",              
            "-acodec", "libmp3lame", 
            "-q:a", "2",        
            "-y",               
            output_audio_path
        ]
        
        
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_audio_path
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        
        try:
            print("FFmpeg tidak ditemukan, menggunakan MoviePy (lebih lambat)...")
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(output_audio_path, codec='mp3', logger=None)
            video.close()
            return output_audio_path
        except Exception as e:
            print(f"Terjadi kesalahan saat mengekstrak audio: {e}")
            return None
    except Exception as e:
        print(f"Terjadi kesalahan sistem: {e}")
        return None