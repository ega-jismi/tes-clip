from moviepy.editor import VideoFileClip
import os

def extract_audio(video_path, output_audio_path):
    """
    Fungsi untuk mengekstrak audio dari video menggunakan MoviePy.
    """
    try:
        # Buka file video
        video = VideoFileClip(video_path)
        
        # Ekstrak audio dan simpan sebagai file mp3
        # logger=None agar terminal kita tidak penuh dengan log proses MoviePy
        video.audio.write_audiofile(output_audio_path, codec='mp3', logger=None)
        
        # Tutup file untuk membersihkan memori (penting untuk mencegah memory leak!)
        video.close()
        
        return output_audio_path
    
    except Exception as e:
        print(f"Terjadi kesalahan saat mengekstrak audio: {e}")
        return None