import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash" 

def analyze_transcript_for_clips(transcript_data, custom_instruction="Menarik", num_clips=1, duration=30):
    """
    Mengirim transkrip ke Gemini dengan instruksi jumlah dan durasi yang dinamis.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        transcript_text = ""
        for item in transcript_data:
            transcript_text += f"[{item['start']:.2f} - {item['end']:.2f}] {item['text']}\n"
        
        # PROMPT YANG DIPERBARUI: Menggunakan num_clips dan duration
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
        
        response = model.generate_content(prompt)
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        clips_data = json.loads(response_text)
        
        # Pastikan kita hanya mengambil jumlah klip yang diminta (untuk keamanan)
        return {"status": "success", "data": clips_data[:num_clips]}
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error Gemini: {error_msg}")
        
        # Menangkap error spesifik kuota (429)
        if "429" in error_msg or "quota" in error_msg.lower() or "rate-limit" in error_msg.lower():
            return {"status": "error_quota", "message": "Kuota API Gemini Anda habis (Limit harian/menit tercapai). Silakan gunakan API Key lain atau tunggu beberapa saat."}
            
        return {"status": "error_general", "message": f"Gagal menganalisis dengan Gemini: {error_msg}"}