from faster_whisper import WhisperModel
import os

def transcribe_audio(audio_path, model_size="base"):
    
    print(f"🚀 Memulai transkripsi lokal dengan model Whisper ({model_size}) di CPU...")
    try:
       
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Lakukan transkripsi
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        print(f"✅ Transkripsi berhasil. Bahasa terdeteksi: '{info.language}' dengan probabilitas {info.language_probability:.2f}")
        
        # Konversi generator segments menjadi list of dictionary sesuai standar sebelumnya
        transcript = []
        for segment in segments:
            transcript.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
            
        return transcript
        
    except Exception as e:
        print(f"❌ Gagal melakukan transkripsi lokal: {e}")
        return None