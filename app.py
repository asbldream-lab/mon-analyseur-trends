import streamlit as st
import os
import re
import yt_dlp
from googleapiclient.discovery import build
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="Video Analyst Pro + Trends", page_icon="📈", layout="wide")

# CSS pour le style
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6 }
    .trend-box { background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px; }
    h1 { color: #FF4B4B; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analyseur de Tendances YouTube")
st.markdown("Analysez jusqu'à **10 vidéos** simultanément pour détecter les vérités qui reviennent tout le temps.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔐 Configuration")
    api_key_youtube = st.text_input("Clé YouTube (AIza...)", type="password")
    api_key_groq = st.text_input("Clé Groq (gsk_...)", type="password")
    st.info("💡 Astuce : Prenez 3-4 vidéos sur le même sujet pour voir la magie opérer.")

# --- FONCTIONS ---
def get_video_id(url):
    if not url: return None
    video_id = re.search(r'(?<=v=)[^&#]+', url)
    if not video_id:
        video_id = re.search(r'(?<=be/)[^&#]+', url)
    return video_id.group(0) if video_id else None

def download_audio_light(url):
    filename = f"audio_{get_video_id(url)}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '64'}],
        'quiet': True,
        'overwrites': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"{filename}.mp3"
    except:
        return None

def get_comments(video_id, api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=40, order="relevance")
        response = request.execute()
        return [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
    except:
        return []

def analyze_with_groq(client, prompt, content, model="llama-3.3-70b-versatile"):
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": f"{prompt}\n\nDATA:\n{content}"}],
            model=model,
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Erreur IA: {e}"

# --- MAIN ---
urls_input = st.text_area("Collez vos liens ici (Max 10) :", height=150, placeholder="https://...\nhttps://...")
launch_btn = st.button("🚀 LANCER L'ANALYSE CROISÉE", type="primary")

if launch_btn:
    urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
    
    # 1. Vérifications de sécurité
    if not api_key_youtube or not api_key_groq:
        st.error("⚠️ Il manque les clés API dans la barre latérale.")
        st.stop()
    
    if len(urls) > 10:
        st.error("⚠️ Pour éviter de surchauffer, on se limite à 10 vidéos maximum !")
        st.stop()

    client = Groq(api_key=api_key_groq)
    global_buffer = [] # Ici on va stocker tous les résumés pour l'analyse finale
    progress_bar = st.progress(0)
    
    st.divider()

    # 2. Boucle d'analyse individuelle
    for i, url in enumerate(urls):
        vid_id = get_video_id(url)
        if not vid_id: continue
        
        with st.status(f"Traitement vidéo {i+1}/{len(urls)} : {url}", expanded=False) as status:
            # A. Transcription
            status.write("👂 Écoute (Whisper)...")
            audio_file = download_audio_light(url)
            if audio_file:
                with open(audio_file, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(audio_file, file.read()),
                        model="whisper-large-v3",
                        response_format="text", language="fr"
                    )
                transcript_text = transcription
                os.remove(audio_file)
            else:
                transcript_text = "Erreur audio"

            # B. Commentaires
            status.write("💬 Commentaires...")
            comments = get_comments(vid_id, api_key_youtube)
            comments_text = "\n".join(comments)

            # C. Résumés unitaires
            status.write("🧠 Analyse unitaire...")
            summary = analyze_with_groq(client, "Résume les points clés factuels en 5 puces.", transcript_text[:15000])
            audience = analyze_with_groq(client, "Résume l'avis général des commentaires en 3 phrases.", comments_text)
            
            # D. Stockage pour le grand final
            data_block = f"""
            --- RAPPORT VIDÉO {i+1} ({url}) ---
            CONTENU : {summary}
            AVIS AUDIENCE : {audience}
            -----------------------------------
            """
            global_buffer.append(data_block)
            
            # E. Affichage discret (Expander) pour ne pas polluer
            with st.expander(f"Voir le détail de la vidéo {i+1}"):
                c1, c2 = st.columns(2)
                c1.info("Contenu"); c1.write(summary)
                c2.warning("Audience"); c2.write(audience)
            
            status.update(label=f"✅ Vidéo {i+1} traitée", state="complete")
        
        progress_bar.progress((i + 1) / len(urls))

    # 3. LE GRAND FINAL : ANALYSE DES TENDANCES
    if len(global_buffer) > 1:
        st.markdown("## 🎯 RÉSULTATS DE L'ANALYSE CROISÉE")
        with st.spinner("🕵️‍♂️ L'IA compare les vidéos entre elles pour trouver les répétitions..."):
            
            all_data = "\n".join(global_buffer)
            
            # C'est ici que la magie opère (Le Prompt de Tendance)
            prompt_trends = f"""
            Tu es un expert en méta-analyse. Je te donne les rapports de {len(urls)} vidéos différentes sur le même sujet.
            
            TA MISSION : Identifier les RÉPÉTITIONS et les CONSENSUS.
            
            Format de réponse attendu (Markdown) :
            
            ### 🔥 Les Faits Incontestables (Ce qui revient partout)
            * (Liste ici les points techniques ou factuels cités dans la majorité des vidéos)
            
            ### 😡 Les Plaintes Récurrentes (Audience)
            * (Ce qui énerve les gens sur plusieurs vidéos. Ex: "Sur 8 vidéos sur 10, les gens se plaignent du prix")
            
            ### ✅ Les Points d'Accord (Audience)
            * (Ce que tout le monde valide)
            
            ### ⚖️ Les Contradictions
            * (Si une vidéo dit blanc et l'autre noir, note-le ici)
            
            Sois précis. Si un point n'apparaît que dans une seule vidéo, IGNORE-LE. Cherche les motifs.
            """
            
            final_trend = analyze_with_groq(client, prompt_trends, all_data)
            
            st.markdown(f'<div class="trend-box">{final_trend}</div>', unsafe_allow_html=True)
            st.balloons()

    elif len(global_buffer) == 1:
        st.warning("Ajoutez au moins 2 vidéos pour débloquer l'analyse de tendances !")