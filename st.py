import streamlit as st
import sys
import os
import base64
import folium
from streamlit_folium import st_folium

sys.path.append(os.path.dirname(__file__))
from graph import app

# ── 페이지 설정 ────────────────────────────────────────────
st.set_page_config(
    page_title="History Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

.stApp {
    background: radial-gradient(ellipse at 50% 0%, #1a2a3a 0%, #0a0f1a 50%, #050810 100%);
    color: #e8eaf0;
    font-family: 'Noto Sans KR', sans-serif;
}
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 2rem !important; max-width: 1200px; }

.hero-title {
    font-family: 'Cinzel', serif;
    font-size: 3.2rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, #ffffff 0%, #a8c8ff 50%, #7eb8f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.05em;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    text-align: center;
    color: #8899bb;
    font-size: 0.95rem;
    margin-bottom: 2.5rem;
    font-weight: 300;
    letter-spacing: 0.1em;
}
.globe-container {
    display: flex;
    justify-content: center;
    margin: 1rem 0 2rem 0;
}
.globe-glow {
    width: 280px;
    height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%,
        #4a7fb5 0%, #2d5f8a 20%, #1a3f60 45%, #0d2030 70%, #050d18 100%
    );
    box-shadow:
        0 0 60px rgba(100,180,255,0.4),
        0 0 120px rgba(70,140,220,0.2),
        inset 0 0 40px rgba(255,255,255,0.05);
    position: relative;
    animation: globePulse 4s ease-in-out infinite;
    border: 1px solid rgba(100,180,255,0.2);
}
.globe-emoji {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 160px;
}
@keyframes globePulse {
    0%, 100% { box-shadow: 0 0 60px rgba(100,180,255,0.4), 0 0 120px rgba(70,140,220,0.2); }
    50%       { box-shadow: 0 0 80px rgba(100,180,255,0.6), 0 0 160px rgba(70,140,220,0.3); }
}

.stTextInput > div > div > input {
    background: rgba(20,35,60,0.8) !important;
    border: 1px solid rgba(100,160,255,0.3) !important;
    border-radius: 50px !important;
    color: #e8eaf0 !important;
    padding: 0.8rem 1.5rem !important;
    font-size: 1rem !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(100,180,255,0.7) !important;
    box-shadow: 0 0 20px rgba(100,180,255,0.2) !important;
}
.stTextInput > div > div > input::placeholder { color: #556688 !important; }

.stButton > button {
    background: linear-gradient(135deg, #1a6abf, #0d4a8f) !important;
    color: white !important;
    border: 1px solid rgba(100,180,255,0.4) !important;
    border-radius: 50px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a7acf, #1a5aaf) !important;
    box-shadow: 0 0 20px rgba(100,180,255,0.4) !important;
}

.section-title {
    font-family: 'Cinzel', serif;
    font-size: 1.2rem;
    color: #a8c8ff;
    letter-spacing: 0.08em;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(100,160,255,0.2);
}

.narration-box {
    background: rgba(10,20,45,0.8);
    border: 1px solid rgba(100,160,255,0.2);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    color: #c8deff;
    font-size: 0.95rem;
    line-height: 1.9;
}

hr { border-color: rgba(100,160,255,0.1) !important; margin: 2rem 0 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── 매핑 ──────────────────────────────────────────────────
FLAG_MAP = {
    "United Kingdom": "🇬🇧",
    "Korea": "🇰🇷",
    "South Korea": "🇰🇷",
    "North Korea": "🇰🇵",
    "Japan": "🇯🇵",
    "China": "🇨🇳",
    "France": "🇫🇷",
    "Germany": "🇩🇪",
    "United States": "🇺🇸",
    "Russia": "🇷🇺",
    "Rome": "🏛️",
    "Ottoman Empire": "🕌",
    "Mongol Empire": "🏹",
    "Spain": "🇪🇸",
    "Portugal": "🇵🇹",
    "Italy": "🇮🇹",
    "Netherlands": "🇳🇱",
    "India": "🇮🇳",
    "Persia": "🏺",
    "Egypt": "🇪🇬",
    "Greece": "🇬🇷",
}

COUNTRY_COORDS = {
    "United Kingdom": (55.3781, -3.4360),
    "Korea": (36.5, 127.9),
    "South Korea": (36.5, 127.9),
    "North Korea": (40.3399, 127.5101),
    "Japan": (36.2048, 138.2529),
    "China": (35.8617, 104.1954),
    "France": (46.2276, 2.2137),
    "Germany": (51.1657, 10.4515),
    "United States": (37.0902, -95.7129),
    "Russia": (61.5240, 105.3188),
    "Rome": (41.9028, 12.4964),
    "Ottoman Empire": (39.9334, 32.8597),
    "Mongol Empire": (46.8625, 103.8467),
    "Spain": (40.4637, -3.7492),
    "Portugal": (39.3999, -8.2245),
    "Italy": (41.8719, 12.5674),
    "Netherlands": (52.1326, 5.2913),
    "India": (20.5937, 78.9629),
    "Persia": (32.4279, 53.6880),
    "Egypt": (26.8206, 30.8025),
    "Greece": (39.0742, 21.8243),
}


def get_flag(country_name: str) -> str:
    return FLAG_MAP.get(country_name, "🌍")


# ── 세션 상태 초기화 ──────────────────────────────────────
if "flat_contents" not in st.session_state:
    st.session_state.flat_contents = []
if "card_image_b64" not in st.session_state:
    st.session_state.card_image_b64 = None
if "narration" not in st.session_state:
    st.session_state.narration = None
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None


# ══════════════════════════════════════════════════════════
# 메인 페이지
# ══════════════════════════════════════════════════════════
st.markdown('<h1 class="hero-title">History Explorer</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">A I &nbsp;·&nbsp; 역사 탐험기</p>', unsafe_allow_html=True
)

st.markdown(
    """
<div class="globe-container">
    <div class="globe-glow">
        <span class="globe-emoji">🌍</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input(
        label="",
        placeholder="🔍  검색: 역사적 사건이나 시대를 입력하세요",
        label_visibility="collapsed",
    )
with col_btn:
    search_clicked = st.button("탐험 시작")


# ══════════════════════════════════════════════════════════
# 파이프라인 실행
# ══════════════════════════════════════════════════════════
if search_clicked and query:
    st.session_state.flat_contents = []
    st.session_state.card_image_b64 = None
    st.session_state.narration = None
    st.session_state.audio_bytes = None

    with st.spinner("역사를 탐험하는 중..."):
        result = app.invoke({"query": query})

    if not result.get("is_valid"):
        st.error(f"❌ {result.get('rejection_reason', '유효하지 않은 쿼리입니다.')}")
    else:
        flat_contents = result.get("answers", [])
        if not flat_contents:
            st.warning("결과를 생성하지 못했습니다.")
        else:
            st.session_state.flat_contents = flat_contents
            st.session_state.card_image_b64 = result.get("card_image_b64")
            st.session_state.narration = result.get("narration")
            st.session_state.audio_bytes = result.get("audio_bytes")


# ══════════════════════════════════════════════════════════
# 결과 표시
# ══════════════════════════════════════════════════════════
if st.session_state.flat_contents:
    flat_contents = st.session_state.flat_contents

    st.divider()

    # ── 지도 ──────────────────────────────────────────────
    st.markdown('<p class="section-title">🗺️ 지도</p>', unsafe_allow_html=True)
    m = folium.Map(zoom_start=2, tiles="CartoDB dark_matter")
    for content in flat_contents:
        coords = COUNTRY_COORDS.get(content.country_name)
        if coords:
            folium.CircleMarker(
                location=coords,
                radius=10,
                color="#4a9eff",
                fill=True,
                fill_color="#4a9eff",
                fill_opacity=0.7,
                popup=folium.Popup(
                    f"<b>{get_flag(content.country_name)} {content.country_name}</b>"
                    f"<br><span style='font-size:0.85rem'>{content.text[:100]}...</span>",
                    max_width=280,
                ),
                tooltip=f"{get_flag(content.country_name)} {content.country_name}",
            ).add_to(m)
    st_folium(m, use_container_width=True, height=380)

    st.divider()

    # ── 카드 이미지 ───────────────────────────────────────
    st.markdown('<p class="section-title">🖼️ 시대 비교 카드</p>', unsafe_allow_html=True)
    if st.session_state.card_image_b64:
        img_bytes = base64.b64decode(st.session_state.card_image_b64)
        st.image(img_bytes, use_container_width=True)
    else:
        st.info("이미지를 생성하지 못했습니다.")

    st.divider()

    # ── 국가별 텍스트 카드 ────────────────────────────────
    st.markdown('<p class="section-title">📋 국가별 내용</p>', unsafe_allow_html=True)
    cols = st.columns(len(flat_contents))
    for col, content in zip(cols, flat_contents):
        with col:
            st.markdown(f"**{get_flag(content.country_name)} {content.country_name}**")
            st.caption(content.text)
            st.caption(f"🎨 _{content.visual_prompt}_")

    st.divider()

    # ── 나레이션 ──────────────────────────────────────────
    st.markdown('<p class="section-title">🔊 나레이션</p>', unsafe_allow_html=True)

    if st.session_state.narration:
        st.markdown(
            f"""
        <div class="narration-box">{st.session_state.narration}</div>
        """,
            unsafe_allow_html=True,
        )

    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/wav")
    else:
        st.info("오디오가 생성되지 않았습니다. graph.py의 TTS 설정을 확인하세요.")
