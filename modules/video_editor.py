import cv2
from moviepy import VideoFileClip, CompositeVideoClip, TextClip
import os
import numpy as np

def process_clip(input_video_path, start_time, end_time, output_filename, aspect_ratio="9:16", transcript=None):
    try:
        video_full = VideoFileClip(input_video_path)
        if start_time >= video_full.duration:
            start_time = max(0, video_full.duration - 5)
        if end_time > video_full.duration:
            end_time = video_full.duration
            
        video = video_full.subclipped(start_time, end_time)

        video_width = video.w
        video_height = video.h
        
        if aspect_ratio == "9:16":
            target_ratio = 9 / 16
            new_width = int(video_height * target_ratio)
            new_height = video_height
        elif aspect_ratio == "1:1":
            new_width = min(video_width, video_height)
            new_height = new_width
        else: # 16:9
            new_width = video_width
            new_height = video_height

        # 2. Deteksi Wajah (Auto-Center)
        mid_time = video.duration / 2
        frame = video.get_frame(mid_time)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, 1.1, 5, minSize=(30, 30))

        center_x = video_width / 2 
        if isinstance(faces, np.ndarray) and len(faces) > 0:
            (x, y, w, h) = faces[0]
            center_x = x + (w / 2)

        # Hitung cropping
        x1 = max(0, int(center_x - (new_width / 2)))
        x2 = min(video_width, x1 + new_width)
        if x2 - x1 < new_width:
            x1 = max(0, video_width - new_width)
            x2 = video_width

        y1 = (video_height - new_height) // 2
        y2 = y1 + new_height

        video = video.cropped(x1=x1, y1=y1, x2=x2, y2=y2)

        # 3. Tambahkan Subtitle (Fitur VEED)
        final_clip = video
        if transcript:
            subtitle_clips = [video]
            relevant_text = [
                item for item in transcript 
                if item['start'] >= start_time and item['end'] <= end_time
            ]
            
            for item in relevant_text:
                local_start = max(0, item['start'] - start_time)
                local_end = min(video.duration, item['end'] - start_time)
                duration = local_end - local_start
                
                if duration > 0:
                    try:
                        txt_clip = TextClip(
                            text=item['text'],
                            font_size=30 if aspect_ratio != "16:9" else 40,
                            color='yellow',
                            font="Arial-Bold",
                            stroke_color="black",
                            stroke_width=1,
                            method='caption',
                            size=(video.w * 0.8, None)
                        ).with_duration(duration).with_position(('center', video.h * 0.8)).with_start(local_start)
                        subtitle_clips.append(txt_clip)
                    except:
                        pass # Lewati jika ImageMagick belum terkonfigurasi
            
            final_clip = CompositeVideoClip(subtitle_clips)

        # 6. Simpan hasil video
        threads_count = os.cpu_count() or 4
        final_clip.write_videofile(
            output_filename, 
            codec="libx264", 
            audio_codec="aac", 
            fps=24, 
            preset="ultrafast",     # Preset ekstrim cepat untuk rendering
            threads=threads_count,  # Menggunakan multi-threading
            logger=None
        )

        video_full.close()
        video.close()
        if transcript: final_clip.close()

        return output_filename

    except Exception as e:
        print(f"Error memproses video: {e}")
        return None