import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))
from graph import app

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
}


def get_flag(country_name: str) -> str:
    return FLAG_MAP.get(country_name, "🌍")


st.set_page_config(page_title="History Explorer", page_icon="🌍", layout="wide")

st.title("🌍 History Explorer")
st.caption("AI 기반 역사 탐험기")

query = st.text_input(
    "탐색할 역사적 주제를 입력하세요",
    placeholder="예: 영국 산업혁명 시기 한국과 일본 상황",
)

if st.button("🔍 탐색하기") and query:
    with st.spinner("파이프라인 실행 중..."):
        result = app.invoke({"query": query})

    if not result.get("is_valid"):
        st.error(f"❌ {result.get('rejection_reason', '유효하지 않은 쿼리입니다.')}")
        st.stop()

    flat_contents = result.get("answers", [])

    if not flat_contents:
        st.warning("결과를 생성하지 못했습니다.")
        st.stop()

    # 이벤트 카드
    st.subheader("📋 국가별 역사 이벤트")
    cols = st.columns(len(flat_contents))
    for col, content in zip(cols, flat_contents):
        with col:
            st.markdown(f"### {get_flag(content.country_name)} {content.country_name}")
            st.write(content.text)
            with st.expander("🎨 Visual Prompt"):
                st.write(content.visual_prompt)

    st.divider()

    # 내러티브
    st.subheader("📝 내러티브")
    for content in flat_contents:
        st.markdown(
            f"**{get_flag(content.country_name)} {content.country_name}**: {content.text}"
        )
