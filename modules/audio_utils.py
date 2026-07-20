import os
import subprocess
from moviepy import VideoFileClip

def extract_audio(video_path, output_audio_path):
    """
    Fungsi untuk mengekstrak audio dari video secara ekstrim cepat menggunakan FFmpeg.
    Jika FFmpeg tidak tersedia, akan menggunakan MoviePy (fallback).
    """
    try:
        # Coba menggunakan FFmpeg secara langsung (jauh lebih cepat, detik vs menit)
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vn",              # Hapus jalur video
            "-acodec", "libmp3lame", # Gunakan codec mp3
            "-q:a", "2",        # Kualitas audio VBR baik
            "-y",               # Timpa file jika sudah ada
            output_audio_path
        ]
        
        # Jalankan command (sembunyikan output)
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_audio_path
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback menggunakan MoviePy jika FFmpeg tidak terpasang di path sistem
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