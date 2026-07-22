import streamlit as st
import os
import time
import base64
from modules.audio_utils import extract_audio
from modules.whisper_ai import transcribe_audio
from modules.gemini_ai import analyze_transcript_for_clips
from modules.video_editor import process_clip

st.set_page_config(page_title="Instant Clip", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

# --- HEADER ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

video_bg_base64 = get_base64_of_bin_file('10469564-uhd_3840_2160_25fps.mp4')
if video_bg_base64:
    st.markdown(f"""
    <style>
    .video-bg {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        min-width: 100vw;
        min-height: 100vh;
        width: auto;
        height: auto;
        z-index: -100;
        object-fit: cover;
        filter: brightness(0.6);
    }}
    </style>
    <video autoplay muted loop class="video-bg" playsinline>
        <source src="data:video/mp4;base64,{video_bg_base64}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

logo_base64 = get_base64_of_bin_file('logo.png')

img_tag = f'<img src="data:image/png;base64,{logo_base64}" alt="Logo" style="height: 120px; object-fit: contain;">' if logo_base64 else ''

st.markdown(f"""
<div class="app-header" style="display: flex; align-items: center; gap: 20px;">
    {img_tag}
    <div>
        <h1 class="app-title" style="margin-bottom: 0;">Instant Clip</h1>
        <p class="app-subtitle" style="margin-top: 10px;">
            <span style="background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 10px; display: inline-block; border: 1px solid rgba(255,255,255,0.2); letter-spacing: 0.5px;">✨ AI-Powered Video Clipper</span><br/>
            Sulap video berdurasi panjang Anda menjadi potongan <strong style="color: #60a5fa; font-weight: 700;">Short, Reel, atau TikTok</strong> yang siap viral hanya dalam hitungan detik.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- CUSTOM CSS UI (Modern, Professional SaaS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Base Font and Global styles */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Animated Gradient Background */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: transparent !important;
    color: #e2e8f0;
}

/* Hide Streamlit Elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="collapsedControl"] { display: none; }
[data-testid="stSidebar"] { display: none; }

/* Typography */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

p, span, label, li {
    color: #cbd5e1 !important;
}

/* Wide Container for less rigid layout */
.block-container {
    padding-top: 3rem !important;
    padding-bottom: 4rem !important;
    max-width: 95% !important; /* Stretch left to right */
    margin: 0 auto;
}

/* Text Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.app-header {
    text-align: left; /* Shift text to left instead of center */
    margin-bottom: 2.5rem;
    padding-top: 1rem;
    animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.app-title {
    font-size: 3.5rem !important;
    background: linear-gradient(90deg, #ffffff, #64748b, #000000, #334155, #ffffff);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    margin-bottom: 0.5rem;
    animation: shine 4s ease-in-out infinite alternate;
}

@keyframes shine {
    0% {
        background-position: 0% center;
    }
    100% {
        background-position: 300% center;
    }
}

.app-subtitle {
    font-size: 1.15rem;
    color: #cbd5e1 !important;
    max-width: 800px;
    line-height: 1.6;
}

/* Glassmorphism for Inputs, Selects, Textareas */
div[data-baseweb="input"] > div, 
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] > div,
div[data-baseweb="number_input"] > div {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
    transition: all 0.3s ease;
}

div[data-baseweb="input"] > div:hover, 
div[data-baseweb="select"] > div:hover,
div[data-baseweb="textarea"]:hover,
div[data-baseweb="number_input"] > div:hover {
    border-color: rgba(255, 255, 255, 0.5) !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

div[data-baseweb="input"] > div:focus-within, 
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="number_input"] > div:focus-within {
    border-color: #ffffff !important;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.2) !important;
}

/* Text inside inputs */
input, textarea, div[data-baseweb="select"] span {
    background-color: transparent !important;
    color: #f8fafc !important;
}

div[data-baseweb="select"] [class*="indicator"] {
    color: #cbd5e1 !important;
}

/* Hide number input +/- buttons */
div[data-baseweb="number_input"] button {
    display: none !important;
}

/* File Uploader Container - Glass */
[data-testid="stFileUploadDropzone"] {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 2px dashed rgba(255, 255, 255, 0.2) !important;
    border-radius: 16px !important;
    padding: 3rem !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

[data-testid="stFileUploadDropzone"]:hover {
    border-color: #ffffff !important;
    background: rgba(255, 255, 255, 0.08) !important;
    box-shadow: 0 10px 30px rgba(255, 255, 255, 0.1) !important;
    transform: translateY(-2px);
}

[data-testid="stFileUploadDropzone"] section {
    background-color: transparent !important;
}

[data-testid="stFileUploadDropzone"] {
    position: relative;
    min-height: 150px;
    display: flex;
    justify-content: center;
    align-items: center;
}

[data-testid="stFileUploadDropzone"] span, 
[data-testid="stFileUploadDropzone"] small, 
[data-testid="stFileUploadDropzone"] button, 
[data-testid="stFileUploadDropzone"] svg {
    display: none !important;
}

[data-testid="stFileUploadDropzone"]::after {
    content: "📥 Klik atau Tarik Video di Sini \\A \\A Maks. 500MB (MP4/MOV)";
    white-space: pre-wrap;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #f8fafc !important;
    font-size: 1.3rem;
    font-weight: 700;
    text-align: center;
    pointer-events: none;
    line-height: 1.2;
    width: 90%;
}

/* Modern Primary Button */
.stButton > button {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2) !important;
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
}

.stButton > button:active {
    transform: translateY(0) scale(0.98);
}

/* Expander - Glass */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    transition: all 0.3s ease;
}

[data-testid="stExpander"]:hover {
    background: rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    color: #f8fafc !important;
}

/* Divider */
hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
    margin: 2.5rem 0 !important;
}

/* Streamlit Status Widget */
[data-testid="stStatusWidget"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

/* Progress bar customization */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, rgba(255,255,255,0.4), rgba(255,255,255,0.9)) !important;
}

/* Animation for step headers */
h3 {
    animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
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
    st.session_state.current_page = "upload"
if 'final_clips' not in st.session_state:
    st.session_state.final_clips = []
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'num_clips' not in st.session_state:
    st.session_state.num_clips = None
if 'duration' not in st.session_state:
    st.session_state.duration = None
if 'aspect_ratio_val' not in st.session_state:
    st.session_state.aspect_ratio_val = "9:16"
if 'whisper_model' not in st.session_state:
    st.session_state.whisper_model = "Biasa Saja (Base)"
if 'selected_model_size' not in st.session_state:
    st.session_state.selected_model_size = "base"
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

if st.session_state.current_page in ["upload", "settings", "prompt", "main"]:
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.markdown("### 🗀 Upload Video")
        uploaded_file = st.file_uploader("Format MP4/MOV - Maks. 500MB", type=["mp4", "mov"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            if uploaded_file.size > 500 * 1024 * 1024:
                st.error("Ukuran file melebihi 500MB. Silakan upload file yang lebih kecil.")
            elif st.session_state.uploaded_file_name != uploaded_file.name:
                TEMP_DIR = "temp"
                os.makedirs(TEMP_DIR, exist_ok=True)
                video_path = os.path.join(TEMP_DIR, uploaded_file.name)
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.video_path = video_path
                st.session_state.uploaded_file_name = uploaded_file.name
                st.rerun() # Refresh to show video preview immediately
        else:
            if st.session_state.video_path is not None:
                st.session_state.video_path = None
                st.session_state.uploaded_file_name = None
                st.rerun()
                
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            st.success(f"Video {st.session_state.uploaded_file_name} berhasil diunggah.")
            st.markdown("---")
            st.markdown("### ⚙️ Penyesuaian Klip")
            
            col_set1, col_set2 = st.columns(2)
            with col_set1:
                num_clips_input = st.text_input("Jumlah klip", value=str(st.session_state.num_clips) if st.session_state.num_clips else "", placeholder="Contoh: 3")
            with col_set2:
                duration_input = st.text_input("Durasi per klip (detik)", value=str(st.session_state.duration) if st.session_state.duration else "", placeholder="Contoh: 30")
            
            ratio_options = ["9:16 (Vertikal - TikTok/Reels)", "Asli (Original)"]
            default_index = 0 if st.session_state.aspect_ratio_val == "9:16" else 1
            aspect_ratio_choice = st.selectbox(
                "Rasio Aspek Output",
                ratio_options,
                index=default_index
            )
            aspect_ratio_val = "9:16" if "9:16" in aspect_ratio_choice else "original"
            
            whisper_options = ["Biasa Saja (Base)", "Jernih (Small)", "Sangat Jernih (Medium)", "Paling Akurat (Large)"]
            default_whisper_idx = whisper_options.index(st.session_state.whisper_model) if st.session_state.whisper_model in whisper_options else 0
            whisper_model = st.selectbox(
                "🎙️ Tingkat keakuratan transkripsi",
                whisper_options,
                index=default_whisper_idx
            )
            
            model_map = {
                "Biasa Saja (Base)": "base",
                "Jernih (Small)": "small",
                "Sangat Jernih (Medium)": "medium",
                "Paling Akurat (Large)": "large"
            }
            selected_model_size = model_map[whisper_model]
            
            st.markdown("### ✨ Instruksi/Prompt Klip")
            prompt = st.text_area(
                "Instruksi/Prompt Klip", 
                placeholder="Misalnya: 'buatkan klip lucu atau motivasi'", 
                value=st.session_state.prompt,
                height=100,
                label_visibility="collapsed"
            )
            
            with st.expander("💡 Ide Prompt untuk Pemula"):
                st.markdown("""
                * **Klip Lucu:** *"Pilihkan momen-momen yang paling lucu, di mana ada tawa atau reaksi kaget."*
                * **Klip Edukasi:** *"Carikan penjelasan yang paling inti dan informatif seperti sedang membagikan tips."*
                * **Klip Motivasi:** *"Ambil bagian yang paling menginspirasi, menyentuh hati, atau memberikan semangat."*
                * **Klip Hook/Viral:** *"Pilih 5 detik pertama yang paling bikin penasaran, diikuti dengan inti cerita."*
                * **Klip Acak (Default):** *"Pilih momen yang paling menarik dan berpotensi viral di media sosial."*
                """)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Buat Klip Sekarang", type="primary", use_container_width=True):
                try:
                    parsed_num = int(num_clips_input) if num_clips_input else 0
                    parsed_dur = int(duration_input) if duration_input else 0
                    
                    if parsed_num <= 0 or parsed_dur <= 0:
                        st.error("⚠️ Silakan masukkan angka yang valid untuk jumlah dan durasi klip.")
                    elif not prompt.strip():
                        st.warning("⚠️ Silakan isi **Instruksi/Prompt Klip** sebelum memulai proses.")
                    else:
                        st.session_state.num_clips = parsed_num
                        st.session_state.duration = parsed_dur
                        st.session_state.aspect_ratio_val = aspect_ratio_val
                        st.session_state.whisper_model = whisper_model
                        st.session_state.selected_model_size = selected_model_size
                        st.session_state.prompt = prompt
                        
                        st.session_state.current_page = "processing"
                        st.session_state.processing_done = False
                        st.session_state.final_clips = []
                        st.rerun()
                except ValueError:
                    st.error("⚠️ Harap masukkan angka yang valid (bukan huruf) untuk jumlah dan durasi klip.")

    with col_right:
        st.markdown("### 📺 Pratinjau Video")
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            st.video(st.session_state.video_path)
        else:
            st.info("Video pratinjau akan muncul di sini setelah Anda mengunggahnya.")

elif st.session_state.current_page == "processing":
    # --- PROCESSING VIEW ---
    st.markdown("### ⚙️ Halaman Proses & Hasil")
    
    # Tombol Kembali
    if st.button("⬅️ Kembali ke Awal", key="back_btn"):
        st.session_state.current_page = "upload"
        st.rerun()

    if not st.session_state.processing_done:
        st.info("Memproses video... Mohon tunggu, proses ini mungkin memakan waktu beberapa menit.")
        start_time_process = time.time()
        
        with st.status("🎬 Memulai proses...", expanded=True) as status:
            TEMP_DIR = "temp"
            # 1. Ekstrak Audio
            st.write("⏳Mengekstrak audio dari video...")
            audio_path = os.path.join(TEMP_DIR, "temp_audio.mp3")
            extract_audio(st.session_state.video_path, audio_path)
            
            # 2. Transkripsi
            st.write(f"🧠 Menganalisis audio dengan Whisper ({st.session_state.whisper_model})...")
            transcript = transcribe_audio(audio_path, model_size=st.session_state.selected_model_size)
            
            if not transcript:
                status.update(label="❌ Gagal: Transkripsi bermasalah", state="error", expanded=True)
                st.error("Gagal melakukan transkripsi audio. Pastikan model berhasil diunduh dan memori mencukupi.")
            else:
                # 3. Analisis Gemini
                st.write("🤖 Memilih momen terbaik dengan Gemini AI...")
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
        st.markdown("Hasil Klip Anda")
        
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
        
        if num_res == 0:
            st.error("⚠️ Gagal membuat klip. Hal ini mungkin karena server kehabisan memori (RAM) saat merender video, API Gemini gagal merespons dengan benar, atau alat rendering tidak didukung di server hosting.")
            st.info("💡 Saran: Coba unggah video dengan durasi yang lebih pendek, kurangi jumlah klip yang diminta, atau jalankan aplikasi ini secara lokal di PC Anda.")
        elif num_res == 1:
            # Jika hanya 1 klip: Teks full-width, Video ditengah
            clip = st.session_state.final_clips[0]
            st.markdown(f"**{clip.get('title', 'Klip 1')}**")
            if 'reason' in clip:
                st.markdown(f"<p style='font-size: 1.05rem; color: #ffffff; font-style: italic; opacity: 0.9;'>Alasan: {clip['reason']}</p>", unsafe_allow_html=True)
            
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
                        st.markdown(f"<p style='font-size: 1.05rem; color: #ffffff; font-style: italic; opacity: 0.9;'>Alasan: {clip['reason']}</p>", unsafe_allow_html=True)
                    
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
