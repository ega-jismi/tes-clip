import cv2
from moviepy.editor import VideoFileClip
import os
import numpy as np  # Kita mengimpor numpy untuk keamanan data

def process_clip(input_video_path, start_time, end_time, output_filename):
    """
    Fungsi untuk memotong video sesuai durasi dan melakukan auto-crop vertikal.
    Sudah dilengkapi dengan proteksi durasi dan proteksi deteksi wajah.
    """
    try:
        # 1. Buka video utama untuk mengecek durasi aslinya
        video_full = VideoFileClip(input_video_path)
        
        # --- SISTEM KEAMANAN DURASI ---
        # Mencegah error jika Gemini halusinasi memberikan waktu di luar batas video asli
        if start_time >= video_full.duration:
            start_time = max(0, video_full.duration - 5)  # Ambil 5 detik terakhir saja
        if end_time > video_full.duration:
            end_time = video_full.duration
            
        # 2. Potong durasi (trim)
        video = video_full.subclip(start_time, end_time)

        # 3. Ambil satu frame di tengah-tengah klip untuk mencari wajah
        mid_time = video.duration / 2
        frame = video.get_frame(mid_time)

        # 4. Inisialisasi AI Deteksi Wajah
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Hitung dimensi dasar
        video_width = video.w
        video_height = video.h
        target_ratio = 9 / 16
        new_width = int(video_height * target_ratio)

        # Titik tengah bawaan (jika wajah tidak ditemukan)
        center_x = video_width / 2 

        # --- SISTEM KEAMANAN OPENCV ---
        # Memastikan data wajah benar-benar berbentuk array dan memiliki isi
        if isinstance(faces, np.ndarray) and len(faces) > 0:
            (x, y, w, h) = faces[0]
            center_x = x + (w / 2) # Geser titik potong ke hidung subjek

        # Hitung batas garis potong
        x1 = max(0, int(center_x - (new_width / 2)))
        x2 = min(video_width, x1 + new_width)

        # Koreksi matematis jika batas potong menabrak ujung kiri/kanan video
        if x2 - x1 < new_width:
            x1 = video_width - new_width
            x2 = video_width

        # 5. Lakukan pemotongan (Cropping) menjadi Vertikal
        cropped_video = video.crop(x1=x1, y1=0, x2=x2, y2=video_height)

        # 6. Simpan hasil video
        cropped_video.write_videofile(output_filename, codec="libx264", audio_codec="aac", logger=None)

        # Bersihkan memori RAM secara tuntas
        video_full.close()
        video.close()
        cropped_video.close()

        return output_filename

    except Exception as e:
        print(f"Error memproses video OpenCV: {e}")
        return None