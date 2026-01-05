"""
YouTube Video Analyzer - Agent IA pour l'analyse de vidéos YouTube
Extrait transcriptions, commentaires, génère des résumés et identifie les tendances
"""

import streamlit as st
import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================

st.set_page_config(
    page_title="🎬 YouTube Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONNALISÉ - DESIGN CLAIR ET LISIBLE
# ============================================================================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Variables CSS - THÈME CLAIR */
    :root {
        --bg-main: #f8fafc;
        --bg-card: #ffffff;
        --bg-card-hover: #f1f5f9;
        --accent-green: #10b981;
        --accent-green-light: #d1fae5;
        --accent-green-dark: #047857;
        --accent-yellow: #f59e0b;
        --accent-yellow-light: #fef3c7;
        --accent-yellow-dark: #b45309;
        --accent-blue: #3b82f6;
        --accent-blue-light: #dbeafe;
        --accent-blue-dark: #1d4ed8;
        --accent-purple: #8b5cf6;
        --accent-purple-light: #ede9fe;
        --accent-purple-dark: #6d28d9;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Global Styles */
    .stApp {
        background: var(--bg-main);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        text-align: center;
        padding: 2rem 0 3rem 0;
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 50%, #8b5cf6 100%);
        border-radius: 0 0 30px 30px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        font-weight: 400;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--border-color);
    }
    
    section[data-testid="stSidebar"] .stTextInput > div > div {
        background: var(--bg-main);
        border: 2px solid var(--border-color);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    section[data-testid="stSidebar"] .stTextInput > div > div:focus-within {
        border-color: var(--accent-green);
        box-shadow: 0 0 0 3px var(--accent-green-light);
    }
    
    /* Card Styles */
    .result-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .card-green {
        border-left: 5px solid var(--accent-green);
        background: linear-gradient(135deg, #ffffff 0%, #ecfdf5 100%);
    }
    
    .card-yellow {
        border-left: 5px solid var(--accent-yellow);
        background: linear-gradient(135deg, #ffffff 0%, #fffbeb 100%);
    }
    
    .card-blue {
        border-left: 5px solid var(--accent-blue);
        background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%);
    }
    
    .card-purple {
        border-left: 5px solid var(--accent-purple);
        background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);
    }
    
    /* Card Headers */
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .card-icon {
        font-size: 1.8rem;
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    .card-subtitle {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin: 0;
    }
    
    /* Badge Styles */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-green {
        background: var(--accent-green-light);
        color: var(--accent-green-dark);
    }
    
    .badge-yellow {
        background: var(--accent-yellow-light);
        color: var(--accent-yellow-dark);
    }
    
    .badge-blue {
        background: var(--accent-blue-light);
        color: var(--accent-blue-dark);
    }
    
    .badge-purple {
        background: var(--accent-purple-light);
        color: var(--accent-purple-dark);
    }
    
    /* Point List Styles */
    .point-item {
        display: flex;
        gap: 14px;
        padding: 14px 18px;
        background: #f8fafc;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }
    
    .point-item:hover {
        background: #f1f5f9;
        border-color: var(--accent-green);
    }
    
    .point-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--accent-green);
        color: #ffffff;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    
    .point-text {
        color: var(--text-primary);
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    /* Comment Analysis Styles */
    .comment-insight {
        padding: 14px 18px;
        background: var(--accent-yellow-light);
        border-left: 4px solid var(--accent-yellow);
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    /* Trend Styles */
    .trend-item {
        padding: 18px;
        background: var(--accent-purple-light);
        border: 2px solid var(--accent-purple);
        border-radius: 12px;
        margin-bottom: 14px;
    }
    
    .trend-title {
        color: var(--accent-purple-dark);
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 1.05rem;
    }
    
    .trend-description {
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    /* Video Title Styles */
    .video-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--accent-blue-dark);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .video-title::before {
        content: "▶";
        font-size: 0.9rem;
        color: var(--accent-blue);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-green) 0%, #059669 100%);
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 2rem;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }
    
    /* TextArea Styles */
    .stTextArea > div > div > textarea {
        background: #ffffff;
        border: 2px solid var(--border-color);
        border-radius: 12px;
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px var(--accent-blue-light);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .stat-item {
        background: #ffffff;
        border: 2px solid var(--border-color);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: var(--shadow);
    }
    
    .stat-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--accent-green);
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Info Box */
    .info-box {
        background: var(--accent-blue-light);
        border: 2px solid var(--accent-blue);
        border-radius: 12px;
        padding: 1rem;
        color: var(--text-primary);
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .info-box strong {
        color: var(--accent-blue-dark);
    }
    
    .info-box a {
        color: var(--accent-blue-dark);
        font-weight: 600;
    }
    
    /* Warning Box */
    .warning-box {
        background: var(--accent-yellow-light);
        border: 2px solid var(--accent-yellow);
        border-radius: 12px;
        padding: 1rem;
        color: var(--text-primary);
        font-size: 0.9rem;
    }
    
    /* Success Box */
    .success-box {
        background: var(--accent-green-light);
        border: 2px solid var(--accent-green);
        border-radius: 12px;
        padding: 1rem;
        color: var(--text-primary);
        font-size: 0.9rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def extract_video_id(url: str) -> str | None:
    """Extrait l'ID de la vidéo YouTube depuis différents formats d'URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def parse_urls(text: str) -> list[str]:
    """Parse les URLs depuis le texte (séparées par virgules ou retours à la ligne)."""
    separators = re.split(r'[,\n]+', text)
    urls = [url.strip() for url in separators if url.strip()]
    return urls


def get_video_info(video_id: str, api_key: str) -> dict | None:
    """Récupère les informations de la vidéo via l'API YouTube."""
    url = f"https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("items"):
            item = data["items"][0]
            return {
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "description": item["snippet"]["description"][:500],
                "views": item["statistics"].get("viewCount", "N/A"),
                "likes": item["statistics"].get("likeCount", "N/A"),
                "comments_count": item["statistics"].get("commentCount", "N/A")
            }
    except Exception as e:
        st.warning(f"⚠️ Impossible de récupérer les infos vidéo: {e}")
    return None


def get_transcript(video_id: str) -> str | None:
    """Récupère la transcription de la vidéo."""
    try:
        # Nouvelle API youtube-transcript-api v1.0+
        ytt_api = YouTubeTranscriptApi()
        
        # Essaie d'abord en français, puis autres langues
        languages_to_try = ['fr', 'en', 'es', 'de', 'it', 'pt']
        
        try:
            transcript = ytt_api.fetch(video_id, languages=languages_to_try)
        except Exception:
            # Si échec avec langues spécifiques, essaie sans préférence
            transcript = ytt_api.fetch(video_id)
        
        if transcript:
            return " ".join([entry.text for entry in transcript])
    except Exception as e:
        st.warning(f"⚠️ Transcription non disponible: {e}")
    return None


def get_comments(video_id: str, api_key: str, max_comments: int = 100) -> list[str]:
    """Récupère les commentaires de la vidéo via l'API YouTube."""
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": api_key,
        "maxResults": min(max_comments, 100),
        "order": "relevance",
        "textFormat": "plainText"
    }
    comments = []
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        for item in data.get("items", []):
            comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment_text)
    except Exception as e:
        st.warning(f"⚠️ Commentaires non disponibles: {e}")
    return comments


def truncate_text(text: str, max_tokens: int = 4000) -> str:
    """Tronque le texte pour respecter la limite de tokens (estimation: 1 token ≈ 4 chars)."""
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text


def smart_chunk_text(text: str, max_tokens: int = 4000) -> list[str]:
    """Découpe intelligemment le texte en chunks respectant la limite de tokens."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return [text]
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


# ============================================================================
# FONCTIONS D'ANALYSE IA (GROQ)
# ============================================================================

def analyze_transcript_10_points(transcript: str, video_title: str, groq_client: Groq) -> str:
    """Génère 10 points clés méconnus à partir de la transcription."""
    truncated = truncate_text(transcript, max_tokens=5000)
    
    prompt = f"""Tu es un expert en analyse de contenu. Analyse cette transcription de la vidéo "{video_title}" et extrais EXACTEMENT 10 points importants que peu de gens connaissent - des "pépites" d'information précieuses.

RÈGLES STRICTES:
- Exactement 10 points, numérotés de 1 à 10
- Chaque point doit être une information surprenante, méconnue ou contre-intuitive
- Sois concis mais informatif (2-3 phrases max par point)
- Utilise un langage accessible
- Base-toi UNIQUEMENT sur le contenu de la transcription

TRANSCRIPTION:
{truncated}

FORMAT DE RÉPONSE (respecte exactement ce format):
1. [Premier point]
2. [Deuxième point]
...
10. [Dixième point]"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de l'analyse: {e}"


def analyze_comments(comments: list[str], video_title: str, groq_client: Groq) -> str:
    """Analyse les commentaires et génère un résumé de l'opinion de l'audience."""
    if not comments:
        return "Aucun commentaire disponible pour cette vidéo."
    
    comments_text = "\n".join([f"- {c[:200]}" for c in comments[:50]])
    truncated = truncate_text(comments_text, max_tokens=3000)
    
    prompt = f"""Tu es un expert en analyse de sentiment et d'opinion. Analyse ces commentaires de la vidéo "{video_title}" et produis un résumé structuré de ce que l'audience exprime.

COMMENTAIRES:
{truncated}

ANALYSE DEMANDÉE:
1. **Sentiment général**: L'audience est-elle positive, négative ou mitigée?
2. **Points appréciés**: Qu'est-ce que les gens aiment le plus?
3. **Critiques principales**: Quelles sont les réserves ou critiques?
4. **Questions fréquentes**: Y a-t-il des interrogations récurrentes?
5. **Insights surprenants**: Des réactions inattendues ou originales?

Sois concis et factuel. Base-toi uniquement sur les commentaires fournis."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de l'analyse des commentaires: {e}"


def analyze_trends(all_comments: dict[str, list[str]], groq_client: Groq) -> str:
    """Identifie les tendances communes entre les commentaires de plusieurs vidéos."""
    if len(all_comments) < 2:
        return "Il faut au moins 2 vidéos pour identifier des tendances communes."
    
    combined_text = ""
    for video_title, comments in all_comments.items():
        sample_comments = comments[:25]
        combined_text += f"\n\n=== Commentaires de '{video_title}' ===\n"
        combined_text += "\n".join([f"- {c[:200]}" for c in sample_comments])
    
    truncated = truncate_text(combined_text, max_tokens=4500)
    
    prompt = f"""Tu es un expert en analyse de tendances sociales. Analyse les commentaires de PLUSIEURS vidéos YouTube et identifie les POINTS COMMUNS - ce que les différentes communautés expriment de similaire.

COMMENTAIRES DE PLUSIEURS VIDÉOS:
{truncated}

ANALYSE DEMANDÉE (IMPORTANT - inclus des citations exactes de commentaires pour illustrer):

1. **Tendances communes**: Quels thèmes, opinions ou préoccupations reviennent dans TOUTES ou la plupart des vidéos?
   → Cite 2-3 commentaires textuellement entre guillemets pour illustrer

2. **Sentiments partagés**: Y a-t-il des émotions ou réactions similaires?
   → Cite 1-2 commentaires représentatifs entre guillemets

3. **Questions récurrentes**: Des interrogations que l'on retrouve partout?
   → Cite les questions exactes posées par les commentateurs

4. **Points de désaccord**: Des sujets où les communautés divergent?
   → Cite des exemples de commentaires opposés

5. **Verbatims marquants**: Cite 3-5 commentaires particulièrement représentatifs ou percutants qui résument bien l'opinion générale (entre guillemets, avec le contexte)

6. **Insight global**: Quelle conclusion peut-on tirer sur ce que les audiences veulent/pensent?

IMPORTANT: 
- Concentre-toi UNIQUEMENT sur ce qui est COMMUN entre les différentes vidéos
- CITE TEXTUELLEMENT des commentaires entre guillemets "..." pour appuyer chaque point
- Indique de quelle vidéo vient chaque citation si pertinent"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de l'analyse des tendances: {e}"


# ============================================================================
# FONCTIONS D'AFFICHAGE
# ============================================================================

def display_10_points(analysis: str, video_title: str):
    """Affiche les 10 points dans des cartes stylisées."""
    st.markdown(f"""
    <div class="result-card card-green">
        <div class="card-header">
            <span class="card-icon">💎</span>
            <div>
                <p class="card-title">10 Pépites Méconnues</p>
                <p class="card-subtitle">{video_title}</p>
            </div>
            <span class="badge badge-green" style="margin-left: auto;">TRANSCRIPTION</span>
        </div>
    """, unsafe_allow_html=True)
    
    lines = analysis.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and re.match(r'^\d+\.', line):
            match = re.match(r'^(\d+)\.\s*(.+)', line)
            if match:
                num, text = match.groups()
                st.markdown(f"""
                <div class="point-item">
                    <span class="point-number">{num}</span>
                    <span class="point-text">{text}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_comments_analysis(analysis: str, video_title: str):
    """Affiche l'analyse des commentaires."""
    st.markdown(f"""
    <div class="result-card card-yellow">
        <div class="card-header">
            <span class="card-icon">💬</span>
            <div>
                <p class="card-title">Analyse des Commentaires</p>
                <p class="card-subtitle">{video_title}</p>
            </div>
            <span class="badge badge-yellow" style="margin-left: auto;">AUDIENCE</span>
        </div>
    """, unsafe_allow_html=True)
    
    lines = analysis.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            if line.startswith('**') or line.startswith('##'):
                clean_line = re.sub(r'[\*#]+', '', line).strip()
                st.markdown(f"<p style='color: var(--accent-yellow); font-weight: 600; margin-top: 1rem;'>{clean_line}</p>", unsafe_allow_html=True)
            elif line.startswith('-') or line.startswith('•'):
                st.markdown(f"<div class='comment-insight'>{line[1:].strip()}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: var(--text-primary); line-height: 1.6;'>{line}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_trends(analysis: str):
    """Affiche l'analyse des tendances."""
    st.markdown(f"""
    <div class="result-card card-purple">
        <div class="card-header">
            <span class="card-icon">📊</span>
            <div>
                <p class="card-title">Tendances Multi-Vidéos</p>
                <p class="card-subtitle">Points communs entre les communautés</p>
            </div>
            <span class="badge badge-purple" style="margin-left: auto;">TENDANCES</span>
        </div>
    """, unsafe_allow_html=True)
    
    lines = analysis.split('\n')
    current_section = ""
    
    for line in lines:
        line = line.strip()
        if line:
            if line.startswith('**') or line.startswith('##'):
                clean_line = re.sub(r'[\*#]+', '', line).strip()
                st.markdown(f"""
                <div class="trend-item">
                    <p class="trend-title">🔮 {clean_line}</p>
                """, unsafe_allow_html=True)
                current_section = "open"
            elif current_section == "open" and (line.startswith('-') or line.startswith('•') or not line.startswith('**')):
                st.markdown(f"<p class='trend-description'>{line.lstrip('-•').strip()}</p>", unsafe_allow_html=True)
            elif line and not line.startswith('**'):
                st.markdown(f"<p style='color: var(--text-primary); line-height: 1.6; margin: 0.5rem 0;'>{line}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎬 YouTube Analyzer</h1>
        <p class="main-subtitle">Extraire les pépites cachées des vidéos YouTube</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Configuration des clés API
    with st.sidebar:
        st.markdown("### 🔐 Configuration API")
        
        st.markdown("""
        <div class="info-box">
            <strong>YouTube API Key</strong><br>
            Obtenez votre clé sur <a href="https://console.cloud.google.com" target="_blank">Google Cloud Console</a>
        </div>
        """, unsafe_allow_html=True)
        youtube_api_key = st.text_input(
            "Clé YouTube (AIza...)",
            type="password",
            placeholder="AIza...",
            help="Clé API YouTube Data v3"
        )
        
        st.markdown("""
        <div class="info-box">
            <strong>Groq API Key</strong><br>
            Obtenez votre clé sur <a href="https://console.groq.com" target="_blank">Groq Console</a>
        </div>
        """, unsafe_allow_html=True)
        groq_api_key = st.text_input(
            "Clé Groq (gsk_...)",
            type="password",
            placeholder="gsk_...",
            help="Clé API Groq pour le modèle LLaMA"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ À propos")
        st.markdown("""
        <div style="color: var(--text-secondary); font-size: 0.85rem; line-height: 1.6;">
        <strong>Fonctionnalités:</strong><br>
        • 💎 10 points méconnus par vidéo<br>
        • 💬 Analyse des commentaires<br>
        • 📊 Tendances multi-vidéos<br>
        • ⚡ Modèle LLaMA 3.3 70B<br>
        </div>
        """, unsafe_allow_html=True)
    
    # Zone principale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔗 URLs des vidéos YouTube")
        urls_input = st.text_area(
            "Collez vos URLs (une par ligne ou séparées par des virgules)",
            height=120,
            placeholder="https://www.youtube.com/watch?v=xxx\nhttps://youtu.be/yyy\nhttps://www.youtube.com/watch?v=zzz",
            help="Vous pouvez analyser plusieurs vidéos en même temps"
        )
    
    with col2:
        st.markdown("### ⚙️ Options")
        analyze_comments_option = st.checkbox("Analyser les commentaires", value=True)
        show_trends = st.checkbox("Afficher les tendances", value=True, help="Nécessite plusieurs vidéos")
        max_comments = st.slider("Nombre max de commentaires", 20, 100, 50)
    
    # Bouton d'analyse
    if st.button("🚀 Analyser les vidéos", use_container_width=True):
        # Validation des clés
        if not youtube_api_key or not youtube_api_key.startswith("AIza"):
            st.error("❌ Veuillez entrer une clé YouTube valide (commence par 'AIza')")
            return
        
        if not groq_api_key or not groq_api_key.startswith("gsk_"):
            st.error("❌ Veuillez entrer une clé Groq valide (commence par 'gsk_')")
            return
        
        if not urls_input.strip():
            st.error("❌ Veuillez entrer au moins une URL YouTube")
            return
        
        # Initialisation du client Groq
        groq_client = Groq(api_key=groq_api_key)
        
        # Parse des URLs
        urls = parse_urls(urls_input)
        video_ids = []
        
        for url in urls:
            vid_id = extract_video_id(url)
            if vid_id:
                video_ids.append((url, vid_id))
            else:
                st.warning(f"⚠️ URL invalide ignorée: {url}")
        
        if not video_ids:
            st.error("❌ Aucune URL YouTube valide trouvée")
            return
        
        # Affichage des stats
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{len(video_ids)}</div>
                <div class="stat-label">Vidéos</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(video_ids) * 10}</div>
                <div class="stat-label">Points à extraire</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">LLaMA 3.3</div>
                <div class="stat-label">Modèle IA</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stockage des résultats pour les tendances
        all_comments_data = {}
        
        # Analyse de chaque vidéo
        for idx, (url, video_id) in enumerate(video_ids):
            st.markdown(f"---")
            
            with st.spinner(f"🔄 Analyse de la vidéo {idx + 1}/{len(video_ids)}..."):
                # Récupération des infos vidéo
                video_info = get_video_info(video_id, youtube_api_key)
                video_title = video_info["title"] if video_info else f"Vidéo {video_id}"
                
                # Affichage du titre
                st.markdown(f"""
                <div class="video-title">{video_title}</div>
                """, unsafe_allow_html=True)
                
                if video_info:
                    st.markdown(f"""
                    <div style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 1rem;">
                        📺 {video_info['channel']} • 👁️ {int(video_info['views']):,} vues • 💬 {video_info['comments_count']} commentaires
                    </div>
                    """, unsafe_allow_html=True)
                
                # Récupération et analyse de la transcription
                transcript = get_transcript(video_id)
                
                if transcript:
                    with st.spinner("💎 Extraction des 10 pépites..."):
                        analysis_10_points = analyze_transcript_10_points(transcript, video_title, groq_client)
                        display_10_points(analysis_10_points, video_title)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        ⚠️ Transcription non disponible pour cette vidéo. L'analyse des 10 points n'est pas possible.
                    </div>
                    """, unsafe_allow_html=True)
                
                # Analyse des commentaires
                if analyze_comments_option:
                    comments = get_comments(video_id, youtube_api_key, max_comments)
                    
                    if comments:
                        all_comments_data[video_title] = comments
                        
                        with st.spinner("💬 Analyse des commentaires..."):
                            comments_analysis = analyze_comments(comments, video_title, groq_client)
                            display_comments_analysis(comments_analysis, video_title)
                    else:
                        st.markdown("""
                        <div class="warning-box">
                            ⚠️ Aucun commentaire disponible pour cette vidéo.
                        </div>
                        """, unsafe_allow_html=True)
        
        # Analyse des tendances (si plusieurs vidéos)
        if show_trends and len(all_comments_data) >= 2:
            st.markdown("---")
            with st.spinner("📊 Analyse des tendances multi-vidéos..."):
                trends_analysis = analyze_trends(all_comments_data, groq_client)
                display_trends(trends_analysis)
        elif show_trends and len(video_ids) >= 2 and len(all_comments_data) < 2:
            st.markdown("""
            <div class="warning-box">
                ⚠️ Impossible d'analyser les tendances: pas assez de vidéos avec des commentaires disponibles.
            </div>
            """, unsafe_allow_html=True)
        
        # Message de fin
        st.markdown("""
        <div class="success-box" style="margin-top: 2rem; text-align: center;">
            ✅ Analyse terminée avec succès!
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
