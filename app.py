import streamlit as st
import os
from modules.audio_utils import extract_audio
from modules.whisper_ai import transcribe_audio
from modules.gemini_ai import analyze_transcript_for_clips
from modules.video_editor import process_clip


# 1. Konfigurasi dasar halaman web
st.set_page_config(page_title="Auto Clipper AI", page_icon="✂️", layout="centered")

# 2. Header UI
st.title("✂️ Auto Clipper AI")
st.write("Unggah video panjang Anda, dan AI akan otomatis mencari momen terbaik untuk dijadikan klip vertikal!")
# --- TAMBAHAN PANEL PENGATURAN DI SIDEBAR ---
st.sidebar.header("⚙️ Pengaturan AI")
# Pilihan Tema untuk Gemini
# PERUBAHAN: Mengganti Selectbox menjadi Text Area (Input Bebas)
instruksi_bebas = st.sidebar.text_area(
    "Ketik Instruksi Khusus (Prompt Bebas):",
    value="Temukan 1 momen paling menarik atau lucu dari video ini.",
    help="Contoh: 'Cari momen saat dia membahas harga', atau 'Potong bagian tutorial instalasinya saja'."
)
# 2. FITUR BARU: Jumlah Klip
jumlah_klip = st.sidebar.number_input(
    "Jumlah Klip yang Ingin Dibuat:",
    min_value=1, max_value=10, value=1
)
# 3. FITUR BARU: Durasi Klip
durasi_klip = st.sidebar.slider(
    "Target Durasi per Klip (detik):",
    min_value=5, max_value=90, value=30
)

# Pilihan Keakuratan untuk Whisper
akurasi_whisper = st.sidebar.select_slider(
    "Tingkat Keakuratan Transkripsi:",
    options=["tiny", "base", "small"],
    value="base",
    help="Tiny = Paling cepat tapi kurang akurat. Small = Lambat tapi sangat presisi."
)
st.sidebar.info("💡 Ubah pengaturan ini sebelum mengklik tombol proses.")

# 3. Persiapan folder sementara (temp)
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# 4. Widget Upload File
uploaded_file = st.file_uploader("Pilih video (MP4, MOV)", type=["mp4", "mov"])

if uploaded_file is not None:
    st.success(f"Video '{uploaded_file.name}' berhasil diunggah!")
    
    # 5. Tombol eksekusi
    if st.button("Mulai Proses Auto-Clip"):
        with st.spinner("Menyimpan video ke sistem..."):
            
            # Simpan file dari memori browser ke hard drive lokal kita
            video_path = os.path.join(TEMP_DIR, uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.info(f"Video tersimpan di: {video_path}")
            
            # Placeholder untuk modul berikutnya
            st.write("🎵 Mengekstrak audio dari video...")
            audio_path = os.path.join(TEMP_DIR, "temp_audio.mp3")
            extracted_audio = extract_audio(video_path, audio_path)
            
            if extracted_audio:
                st.success("Ekstraksi audio selesai!")
                
                # --- MODUL 2: TRANSKRIPSI AI ---
                st.write("🤖 AI sedang mentranskripsi audio (ini mungkin memakan waktu beberapa menit)...")
                transcript = transcribe_audio(extracted_audio, model_size=akurasi_whisper)
                
                st.success("Transkripsi Selesai!")
                
                # Tampilkan hasil transkripsi ke layar untuk menguji
                st.write("### Hasil Transkripsi:")
                st.json(transcript) # Tampilkan format JSON agar kita bisa melihat timestamp-nya
                st.write("🧠 Mengirim transkrip ke Gemini untuk mencari momen viral...")
                
                # Cari baris ini dan perbarui:
                clips_suggestion = analyze_transcript_for_clips(
                    transcript, 
                    custom_instruction=instruksi_bebas,
                    num_clips=jumlah_klip,
                    duration=durasi_klip
                )               
                if clips_suggestion:
                    st.success("Momen terbaik berhasil ditemukan!")
                    st.write("### Rekomendasi Klip dari AI:")
                    
                    # Tampilkan hasil dari Gemini dengan tampilan yang rapi
                    for i, clip in enumerate(clips_suggestion):
                        st.info(f"**Klip {i+1}: {clip.get('title', 'Tanpa Judul')}**")
                        st.write(f"⏱ Waktu: Detik ke-{clip['start']} s/d {clip['end']}")
                        st.write(f"💡 Alasan: {clip.get('reason', '')}")
                        
                    st.warning("Tahap selanjutnya: OpenCV akan memotong video berdasarkan waktu di atas.")
                    # --- MODUL 4: AUTO-EDITING & CROPPING ---
                    st.write("🎬 Mulai memotong video dan melakukan Auto-Center pada wajah...")
                    
                    # Buat progress bar
                    progress_text = "Memproses klip..."
                    my_bar = st.progress(0, text=progress_text)
                    
                    total_clips = len(clips_suggestion)
                    
                    for i, clip in enumerate(clips_suggestion):
                        st.write(f"Memproses Klip {i+1}: {clip.get('title', 'Tanpa Judul')}...")
                        
                        # Tentukan nama file output
                        output_filename = os.path.join(TEMP_DIR, f"final_clip_{i+1}.mp4")
                        
                        # Panggil fungsi potong OpenCV kita!
                        result_path = process_clip(
                            input_video_path=video_path,
                            start_time=clip['start'],
                            end_time=clip['end'],
                            output_filename=output_filename
                        )
                        
                        if result_path:
                            st.success(f"✅ Klip {i+1} selesai!")
                            # Putar video hasil jadinya langsung di website!
                            st.video(result_path)
                            # Membaca file video yang sudah jadi
                            with open(result_path, "rb") as file:
                                btn = st.download_button(
                                    label=f"⬇️ Unduh Klip {i+1}",
                                    data=file,
                                    file_name=f"auto_clip_{i+1}.mp4",
                                    mime="video/mp4"
                                )
                            
                        # Update progress bar
                        my_bar.progress((i + 1) / total_clips, text=progress_text)
                        
                    st.balloons() # Efek balon perayaan karena aplikasi selesai!
                    st.success("🎉 Semua proses Auto-Clipper berhasil diselesaikan!")
                    # --- CLEAN UP (PEMBERSIHAN) ---
                    st.write("🧹 Membersihkan file sementara...")
                    try:
                        # Hapus audio sementara
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                        # Hapus video asli
                        if os.path.exists(video_path):
                            os.remove(video_path)
                        st.write("✅ Ruang penyimpanan berhasil dibersihkan!")
                    except Exception as e:
                        st.write(f"Gagal membersihkan beberapa file: {e}")
                else:
                    st.error("Gagal mendapatkan rekomendasi dari Gemini. Cek koneksi atau API Key.")
                
            else:
                st.error("Gagal mengekstrak audio.")
                        
                
            