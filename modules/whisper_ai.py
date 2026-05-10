from gradio_client import Client, handle_file
import os
import json  # Library wajib untuk membedah file JSON dari Gradio
from dotenv import load_dotenv

load_dotenv()

# Kita tetap menerima model_size dari UI Streamlit Anda
def transcribe_audio(audio_path, model_size="base"):
    url = os.getenv("COLAB_URL")
    
    if not url:
        print("Error: COLAB_URL belum diisi di file .env!")
        return None

    print("🚀 Mengirim audio ke Server Google Colab (GPU)...")
    try:
        client = Client(url)
        
        # Menerima hasil dari Colab
        result = client.predict(
            audio_path=handle_file(audio_path),
            api_name="/predict"
        )
        
        print("✅ Respons diterima dari Colab, memproses data...")
        
        # --- SISTEM PENERJEMAH DATA GRADIO ---
        
        # Skenario 1: Jika Colab mengirimkan sebuah "alamat file .json"
        if isinstance(result, str) and result.endswith('.json'):
            with open(result, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
            
        # Skenario 2: Jika Colab mengirimkan teks JSON mentah
        if isinstance(result, str):
            # Mencoba mengubah teks menjadi data Python
            return json.loads(result)
            
        # Skenario 3: Jika Colab sudah berbaik hati mengirimkan data murni (List/Dict)
        return result
        
    except Exception as e:
        print(f"❌ Gagal menghubungi Colab atau memproses data: {e}")
        return None