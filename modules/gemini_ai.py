from google import genai
import os
from dotenv import load_dotenv
import json

# Memuat variabel rahasia dari file .env
load_dotenv()

# Gunakan SDK google-genai yang baru
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Gunakan versi model yang terdaftar secara resmi
MODEL_NAME = "gemini-2.5-flash" 

def analyze_transcript_for_clips(transcript_data, custom_instruction="Menarik", num_clips=1, duration=30):
    """
    Mengirim transkrip ke Gemini dengan instruksi jumlah dan durasi yang dinamis.
    """
    try:
        transcript_text = ""
        for item in transcript_data:
            transcript_text += f"[{item['start']:.2f} - {item['end']:.2f}] {item['text']}\n"
        
        prompt = f"""
        Anda adalah editor video profesional.
        Tugas Anda:
        1. Berdasarkan transkrip di bawah, temukan TEPAT {num_clips} klip video.
        2. Instruksi khusus konten: "{custom_instruction}"
        3. Setiap klip harus memiliki durasi SEKITAR {duration} detik.
        4. KEMBALIKAN JAWABAN HANYA DALAM FORMAT JSON SEPERTI CONTOH BERIKUT:
        
        [
            {{
                "start": 10.0,
                "end": {10.0 + duration},
                "title": "Judul Klip",
                "reason": "Alasan memilih bagian ini"
            }}
        ]
        
        Transkrip:
        {transcript_text}
        """
        
        # Panggilan SDK google-genai yang baru
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        clips_data = json.loads(response_text)
        
        return {"status": "success", "data": clips_data[:num_clips]}
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error Gemini: {error_msg}")
        
        if "429" in error_msg or "quota" in error_msg.lower() or "rate-limit" in error_msg.lower():
            return {"status": "error_quota", "message": "Kuota API Gemini Anda habis (Limit harian/menit tercapai). Silakan gunakan API Key lain atau tunggu beberapa saat."}
            
        return {"status": "error_general", "message": f"Gagal menganalisis dengan Gemini: {error_msg}"}