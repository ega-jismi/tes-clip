import os
from moviepy import TextClip, CompositeVideoClip, ColorClip

def create_subtitle_clip(text, duration, video_w, video_h, fontsize=40, color='yellow'):
    """
    Membuat klip teks subtitle sederhana.
    """
    try:
        # Membuat klip teks
        # Catatan: MoviePy v2.x menggunakan argumen yang sedikit berbeda
        txt_clip = TextClip(
            text=text,
            font_size=fontsize,
            color=color,
            font="Arial-Bold", # Pastikan font ini ada di sistem atau gunakan font standar
            stroke_color="black",
            stroke_width=2,
            method='caption',
            size=(video_w * 0.8, None)
        ).with_duration(duration).with_position(('center', video_h * 0.8))
        
        return txt_clip
    except Exception as e:
        print(f"Error creating subtitle: {e}")
        return None

def apply_subtitles_to_clip(video_clip, transcript_segment, start_time):
    """
    Menambahkan subtitle ke klip video berdasarkan potongan transkrip yang relevan.
    """
    subtitle_clips = [video_clip]
    
    # Filter transkrip yang masuk dalam rentang waktu klip ini
    clip_end = start_time + video_clip.duration
    
    relevant_text = [
        item for item in transcript_segment 
        if item['start'] >= start_time and item['end'] <= clip_end
    ]
    
    for item in relevant_text:
        duration = item['end'] - item['start']
        # Sesuaikan waktu mulai teks agar relatif terhadap awal klip
        local_start = item['start'] - start_time
        
        txt_clip = create_subtitle_clip(
            item['text'], 
            duration, 
            video_clip.w, 
            video_clip.h
        )
        
        if txt_clip:
            subtitle_clips.append(txt_clip.with_start(local_start))
            
    return CompositeVideoClip(subtitle_clips)
