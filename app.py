import streamlit as st
import os
import time
from modules.audio_utils import extract_audio
from modules.whisper_ai import transcribe_audio
from modules.gemini_ai import analyze_transcript_for_clips
from modules.video_editor import process_clip

st.set_page_config(page_title="Instant Clip", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

# --- HEADER ---
st.title("🎬 Instant Clip")
st.markdown("Ubah video panjang Anda menjadi klip-klip pendek menarik dalam hitungan menit.")

# --- CUSTOM CSS UI (Modern, Glassmorphism, Animations) ---
st.markdown("""
<style>
/* Hide the sidebar completely */
[data-testid="collapsedControl"] { display: none; }
[data-testid="stSidebar"] { display: none; }

/* Animated Gradient Background */
.stApp {
    background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #1e1b4b);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: white;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

h1, h2, h3, p, span, label, li {
    color: white !important;
}

/* Modern Button Styling with Animation */
.stButton > button {
    transition: all 0.3s ease;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7e22ce 100%) !important;
    color: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(126, 34, 206, 0.4) !important;
    background: linear-gradient(135deg, #4338ca 0%, #6b21a8 100%) !important;
}

.stButton > button:active {
    transform: translateY(1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
}

/* Input Fields & Textareas Glassmorphism */
div[data-baseweb="input"] > div, 
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] > div,
div[data-baseweb="number_input"] > div {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    color: white !important;
    transition: all 0.3s ease;
}

/* Force transparency on ALL inner components of inputs (especially number_input +/- buttons and input box) */
div[data-baseweb="input"] *, 
div[data-baseweb="number_input"] *,
div[data-testid="stFileUploader"] section {
    background-color: transparent !important;
}

/* Make actual text inputs transparent to inherit the glass wrapper */
input, textarea, div[data-baseweb="select"] span {
    background-color: transparent !important;
    color: white !important;
}

/* Hide the +/- buttons in number inputs for manual typing only */
div[data-baseweb="number_input"] button {
    display: none !important;
}

div[data-baseweb="input"] > div:hover, 
div[data-baseweb="select"] > div:hover,
div[data-baseweb="textarea"]:hover,
div[data-baseweb="number_input"] > div:hover {
    border-color: rgba(168, 85, 247, 0.4) !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
}

div[data-baseweb="input"] > div:focus-within, 
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="number_input"] > div:focus-within {
    border-color: #a855f7 !important;
    box-shadow: 0 0 8px rgba(168, 85, 247, 0.2) !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
}

/* Uploader Container Styling (Fixing the black box) */
[data-testid="stFileUploadDropzone"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 2px dashed rgba(255, 255, 255, 0.2) !important;
    border-radius: 15px !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.3s ease;
}

[data-testid="stFileUploadDropzone"]:hover {
    border-color: #a855f7 !important;
    background-color: rgba(168, 85, 247, 0.05) !important;
}

/* Expander Glassmorphism */
[data-testid="stExpander"] {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(5px);
}
</style>
""", unsafe_allow_html=True)

# CSS tambahan untuk membatasi ukuran tinggi video yang ditampilkan (khususnya 9:16)
st.markdown("""
<style>
    div[data-testid="stVideo"] {
        max-height: 500px !important;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stVideo"] video {
        max-height: 450px !important;
        width: auto !important;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- STATE MANAGEMENT ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "input"
if 'final_clips' not in st.session_state:
    st.session_state.final_clips = []
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False

if st.session_state.current_page == "input":
    # --- SETTINGS SECTION ---
    st.markdown("### ⚙️ Pengaturan Dasar")
    col_set1, col_set2, col_set3 = st.columns(3)
    
    with col_set1:
        num_clips = st.number_input("Jumlah klip yang ingin dibuat", min_value=1, max_value=20, value=None, placeholder="Masukkan angka (contoh: 3)")
        
    with col_set2:
        duration = st.number_input("Target durasi per klip (detik)", min_value=10, max_value=300, value=None, step=1, placeholder="Masukkan angka (contoh: 30)")
    
    with col_set3:
        aspect_ratio_choice = st.selectbox(
            "Rasio Aspek Output",
            ["9:16 (Vertikal - TikTok/Reels)", "Asli (Original)"],
            index=0,
            help="Pilih ukuran video hasil akhir."
        )
        aspect_ratio_val = "9:16" if "9:16" in aspect_ratio_choice else "original"
    
    whisper_model = st.selectbox(
        "🎙️ Tingkat keakuratan transkripsi (Whisper)",
        ["Biasa Saja (Base)", "Jernih (Small)", "Sangat Jernih (Medium)", "Paling Akurat (Large)"],
        index=0,
        help="Pilih tingkat keakuratan. Semakin akurat (jernih), semakin lama waktu pemrosesan."
    )
    
    model_map = {
        "Biasa Saja (Base)": "base",
        "Jernih (Small)": "small",
        "Sangat Jernih (Medium)": "medium",
        "Paling Akurat (Large)": "large"
    }
    selected_model_size = model_map[whisper_model]
    
    st.markdown("<hr style='opacity: 0.2;'>", unsafe_allow_html=True)
    
    # --- UPLOAD & PROMPT SECTION ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📂 Upload Video")
        uploaded_file = st.file_uploader("Format MP4/MOV - Maks. 500MB", type=["mp4", "mov"], label_visibility="collapsed")
    
    with col2:
        st.markdown("### ✨ Instruksi/Prompt Klip")
        prompt = st.text_area(
            "Instruksi/Prompt Klip", 
            placeholder="Misalnya: 'buatkan klip lucu atau motivasi'", 
            value="",
            height=130,
            label_visibility="collapsed"
        )
        
        with st.expander("💡 Ide Prompt untuk Pemula"):
            st.markdown("""
            Bingung mau tulis apa? Coba *copy-paste* salah satu kalimat di bawah ini:
            
            * **Klip Lucu:** *"Pilihkan momen-momen yang paling lucu, di mana ada tawa atau reaksi kaget."*
            * **Klip Edukasi:** *"Carikan penjelasan yang paling inti dan informatif seperti sedang membagikan tips."*
            * **Klip Motivasi:** *"Ambil bagian yang paling menginspirasi, menyentuh hati, atau memberikan semangat."*
            * **Klip Hook/Viral:** *"Pilih 5 detik pertama yang paling bikin penasaran, diikuti dengan inti cerita."*
            * **Klip Acak (Default):** *"Pilih momen yang paling menarik dan berpotensi viral di media sosial."*
            """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BUTTON START PROCESSING ---
    if st.button("🚀 Buat Klip Sekarang", type="primary", use_container_width=True):
        if not num_clips:
            st.warning("⚠️ Silakan isi **Jumlah klip yang ingin dibuat** pada bagian Pengaturan di atas.")
        elif not duration:
            st.warning("⚠️ Silakan isi **Target durasi per klip** pada bagian Pengaturan di atas.")
        elif not prompt.strip():
            st.warning("⚠️ Silakan isi **Instruksi/Prompt Klip** sebelum memulai proses.")
        elif uploaded_file is None:
            st.error("Silakan upload video terlebih dahulu.")
        elif uploaded_file.size > 500 * 1024 * 1024:
            st.error("Ukuran file melebihi 500MB. Silakan upload file yang lebih kecil.")
        else:
            # Pindah ke tab processing dan simpan konfigurasi
            TEMP_DIR = "temp"
            os.makedirs(TEMP_DIR, exist_ok=True)
            video_path = os.path.join(TEMP_DIR, uploaded_file.name)
            
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.video_path = video_path
            st.session_state.num_clips = num_clips
            st.session_state.duration = duration
            st.session_state.aspect_ratio_val = aspect_ratio_val
            st.session_state.selected_model_size = selected_model_size
            st.session_state.whisper_model = whisper_model
            st.session_state.prompt = prompt
            st.session_state.current_page = "processing"
            st.session_state.processing_done = False
            st.session_state.final_clips = []
            st.rerun()

elif st.session_state.current_page == "processing":
    # --- PROCESSING VIEW ---
    st.markdown("### ⚙️ Halaman Proses & Hasil")
    
    # Tombol Kembali
    if st.button("⬅️ Kembali ke Pengaturan", key="back_btn"):
        st.session_state.current_page = "input"
        st.rerun()

    if not st.session_state.processing_done:
        st.info("Memproses video... Mohon tunggu, proses ini mungkin memakan waktu beberapa menit.")
        start_time_process = time.time()
        
        with st.status("🎬 Memulai proses...", expanded=True) as status:
            TEMP_DIR = "temp"
            # 1. Ekstrak Audio
            st.write("⏳ **Langkah 1/4:** Mengekstrak audio dari video...")
            audio_path = os.path.join(TEMP_DIR, "temp_audio.mp3")
            extract_audio(st.session_state.video_path, audio_path)
            
            # 2. Transkripsi
            st.write(f"🧠 **Langkah 2/4:** Menganalisis audio dengan Whisper ({st.session_state.whisper_model})...")
            transcript = transcribe_audio(audio_path, model_size=st.session_state.selected_model_size)
            
            if not transcript:
                status.update(label="❌ Gagal: Transkripsi bermasalah", state="error", expanded=True)
                st.error("Gagal melakukan transkripsi audio. Pastikan model berhasil diunduh dan memori mencukupi.")
            else:
                # 3. Analisis Gemini
                st.write("🤖 **Langkah 3/4:** Memilih momen terbaik dengan Gemini AI...")
                gemini_result = analyze_transcript_for_clips(
                    transcript, 
                    custom_instruction=st.session_state.prompt, 
                    num_clips=st.session_state.num_clips, 
                    duration=st.session_state.duration
                )
                
                if gemini_result["status"] != "success":
                    status.update(label="❌ Gagal: AI Error", state="error", expanded=True)
                    if gemini_result["status"] == "error_quota":
                        st.error("⚠️ **Peringatan Kuota:** " + gemini_result["message"])
                    else:
                        st.error(gemini_result["message"])
                else:
                    clips_suggestion = gemini_result["data"]
                    # 4. Potong Video & Tambah Subtitle
                    st.write("✂️ **Langkah 4/4:** Memotong video dan menambahkan subtitle...")
                    
                    final_clips = []
                    clip_progress = st.progress(0, text="Menyiapkan perenderan klip pertama...")
                    total_clips = len(clips_suggestion)
                    
                    start_render_time = time.time()
                    
                    for i, clip in enumerate(clips_suggestion):
                        st.write(f"▶️ Merender klip {i+1} dari {total_clips}...")
                        out = os.path.join(TEMP_DIR, f"final_clip_{i+1}.mp4")
                        
                        res = process_clip(
                            input_video_path=st.session_state.video_path, 
                            start_time=clip['start'], 
                            end_time=clip['end'], 
                            output_filename=out, 
                            aspect_ratio=st.session_state.aspect_ratio_val, 
                            transcript=transcript
                        )
                        
                        if res:
                            clip['path'] = res
                            final_clips.append(clip)
                        
                        elapsed_time = time.time() - start_render_time
                        avg_time_per_clip = elapsed_time / (i + 1)
                        remaining_clips = total_clips - (i + 1)
                        eta_seconds = int(avg_time_per_clip * remaining_clips)
                        
                        if remaining_clips > 0:
                            eta_m, eta_s = divmod(eta_seconds, 60)
                            if eta_m > 0:
                                eta_str = f"{eta_m} menit {eta_s} detik"
                            else:
                                eta_str = f"{eta_seconds} detik"
                            progress_text = f"Memproses: {i+1}/{total_clips} klip. ⏳ Estimasi selesai dalam {eta_str}..."
                        else:
                            progress_text = f"Selesai memproses {total_clips} klip! 🎉"
                        
                        clip_progress.progress((i + 1) / total_clips, text=progress_text)
                    
                    end_time_process = time.time()
                    time_taken = int(end_time_process - start_time_process)
                    status.update(label=f"Selesai dalam {time_taken} detik! 🎉", state="complete", expanded=False)
                    
                    st.session_state.final_clips = final_clips
                    st.session_state.processing_done = True
                    
                    st.balloons()
                    st.success("Klip berhasil dibuat!")
                    st.rerun() # Refresh to hide processing spinners and purely show results
                    
    if st.session_state.processing_done:
        # Menampilkan Hasil
        st.markdown("---")
        st.markdown("### 🎉 Hasil Klip Anda")
        
        # Tambahan CSS untuk membingkai video dengan rapi
        st.markdown("""
        <style>
            [data-testid="stVideo"] {
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Layout dinamis agar hasil selalu di tengah (centered)
        # Menyesuaikan jumlah klip agar tidak ada ruang kosong yang aneh di desktop
        num_res = len(st.session_state.final_clips)
        
        if num_res == 1:
            # Jika hanya 1 klip: Teks full-width, Video ditengah
            clip = st.session_state.final_clips[0]
            st.markdown(f"**{clip.get('title', 'Klip 1')}**")
            if 'reason' in clip:
                st.caption(f"*Alasan: {clip['reason']}*")
            
            # Buat kolom hanya untuk menengahkan video
            if st.session_state.aspect_ratio_val == "9:16":
                _, center_vid, _ = st.columns([1, 1, 1])
            else:
                _, center_vid, _ = st.columns([1, 2.5, 1])
                
            with center_vid:
                st.video(clip['path'])
                with open(clip['path'], "rb") as file:
                    st.download_button(
                        label="⬇️ Unduh Klip 1",
                        data=file,
                        file_name="instant_clip_1.mp4",
                        mime="video/mp4",
                        key="download_0",
                        use_container_width=True
                    )
            st.markdown("<br>", unsafe_allow_html=True)
            
        else:
            # Jika 2 klip atau lebih, gunakan grid/kolom untuk seluruh elemen
            if num_res == 2:
                _, col1, col2, _ = st.columns([1, 3, 3, 1])
                cols = [col1, col2]
            else:
                cols = st.columns(3)
                
            for i, clip in enumerate(st.session_state.final_clips):
                col = cols[i % len(cols)]
                with col:
                    st.markdown(f"**{clip.get('title', f'Klip {i+1}')}**")
                    if 'reason' in clip:
                        st.caption(f"*Alasan: {clip['reason']}*")
                    
                    st.video(clip['path'])
                    
                    with open(clip['path'], "rb") as file:
                        st.download_button(
                            label=f"⬇️ Unduh Klip {i+1}",
                            data=file,
                            file_name=f"instant_clip_{i+1}.mp4",
                            mime="video/mp4",
                            key=f"download_{i}",
                            use_container_width=True
                        )
                    st.markdown("<br>", unsafe_allow_html=True)
