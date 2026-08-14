"""
일어나 파트라슈 — AI 음성 파트라슈 통합본

기존 기능
- 체중관리
- 건강체크
- 복약알리미
- 케어기록
- 광고 배너

추가 기능
- Gemini 모델 선택
- 마이크 음성 입력
- Gemini 음성 → 텍스트
- 강아지 프로필/기록을 참고한 AI 케어 답변
- gTTS 음성 답변
- 이전 대화 기억
"""

from __future__ import annotations

import base64
import hashlib
from datetime import date
from io import BytesIO
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from gtts import gTTS


# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="일어나 파트라슈",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
PHOTO_DIR = BASE_DIR / "files" / "photo"

MODEL_OPTIONS = {
    "Gemini 3.6 Flash · 추천": "gemini-3.6-flash",
    "Gemini 3.5 Flash-Lite · 빠름": "gemini-3.5-flash-lite",
}

BREEDS = ["믹스견", "말티즈", "푸들", "시바견", "진돗개", "기타"]

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None


# ============================================================
# 디자인
# ============================================================

CUSTOM_CSS = """
<style>
    :root { color-scheme: light !important; }

    html, body, .stApp,
    [data-testid="stAppViewContainer"] {
        background: #FFF6EE !important;
        color: #4A3B32 !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        color: #4A3B32;
        font-size: 2.45rem;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin-bottom: 0.2rem;
    }

    .main-sub {
        color: #B5705A;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFEADC !important;
    }

    section[data-testid="stSidebar"] * {
        color: #4A3B32;
    }

    .stButton > button {
        background-color: #FF8C69;
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
    }

    .stButton > button:hover {
        background-color: #FF7A52;
        color: white !important;
        border: none;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #FFE3D3;
        border-radius: 10px 10px 0 0;
        color: #4A3B32;
        font-weight: 650;
        padding: 10px 18px;
        justify-content: center;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FF8C69 !important;
        color: white !important;
    }

    .ai-hero {
        background: linear-gradient(135deg, #FFF0E5 0%, #FFE4D3 100%);
        border: 1px solid #FFD2BD;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }

    .ai-kicker {
        color: #E96F4D;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        margin-bottom: 5px;
    }

    .ai-title {
        color: #4A3B32;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .ai-desc {
        color: #8B6657;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .mini-card {
        background: rgba(255,255,255,0.72);
        border: 1px solid #F2D8C8;
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    div[data-testid="stChatMessage"] {
        background: #FFFDFC !important;
        border: 1px solid #F0D9CC;
        border-radius: 15px;
        color: #4A3B32 !important;
    }

    div[data-testid="stChatMessage"] * {
        color: #4A3B32 !important;
    }

    [data-testid="stAlert"] *,
    [data-testid="stStatusWidget"] *,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stCaptionContainer"] {
        color: #4A3B32;
    }

    .medical-note {
        color: #8A7368;
        font-size: 0.79rem;
        line-height: 1.5;
        margin-top: 10px;
    }

    @media (max-width: 760px) {
        .main-title { font-size: 2rem; }
        .block-container { padding-top: 1rem; }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 10px;
            font-size: 0.83rem;
        }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# 상태 관리
# ============================================================

def init_state():
    defaults = {
        "dog_name": "파트라슈",
        "dog_age": 8,
        "dog_breed": "믹스견",
        "weight_log": [],
        "health_history": [],
        "medicines": [],
        "med_check_today": {},
        "care_log": [],

        # AI 음성 파트라슈
        "ai_chat": [],
        "ai_messages": [],
        "ai_processed_signature": None,
        "ai_answer_audio": None,
        "ai_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()
ss = st.session_state


# ============================================================
# 공통 유틸
# ============================================================

def senior_stage(age: int) -> str:
    """기존 앱과 동일한 단순 데모 기준."""
    if age >= 11:
        return "🟠 노령기"
    if age >= 7:
        return "🟡 시니어 진입"
    return "🟢 성인기"


def safe_image(path: Path, *, use_container_width=True):
    if path.exists():
        st.image(str(path), use_container_width=use_container_width)
        return True
    st.caption(f"이미지를 찾을 수 없어요: {path.name}")
    return False


def latest_dog_context() -> str:
    """AI가 현재 앱의 기록을 참고할 수 있도록 짧은 문맥을 생성."""
    last_weight = ss.weight_log[-1]["체중"] if ss.weight_log else None
    last_health = ss.health_history[-1] if ss.health_history else None
    last_care = ss.care_log[-1] if ss.care_log else None

    if ss.medicines:
        med_text = ", ".join(
            f"{m['시간']} {m['이름']}" for m in ss.medicines
        )
    else:
        med_text = "등록된 복약 없음"

    context_lines = [
        f"반려견 이름: {ss.dog_name}",
        f"나이: {ss.dog_age}세",
        f"견종: {ss.dog_breed}",
        f"앱 표시 단계: {senior_stage(ss.dog_age)}",
        f"최근 체중: {last_weight}kg" if last_weight is not None else "최근 체중 기록 없음",
        (
            f"최근 건강체크: {last_health['점수']}점 / {last_health['판정']}"
            if last_health else "최근 건강체크 기록 없음"
        ),
        f"복약 등록: {med_text}",
        (
            f"최근 케어기록: 산책 {last_care['산책분']}분 / 메모: {last_care['메모']}"
            if last_care else "최근 케어기록 없음"
        ),
    ]
    return "\n".join(context_lines)


# ============================================================
# Gemini + TTS
# ============================================================

def gemini_client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Gemini API Key가 설정되지 않았습니다. "
            "Streamlit Cloud의 App settings → Secrets에 "
            'GEMINI_API_KEY = "..." 를 등록해 주세요.'
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def transcribe_audio(audio_bytes: bytes, model_name: str) -> str:
    client = gemini_client()

    response = client.models.generate_content(
        model=model_name,
        contents=[
            (
                "다음 오디오에서 보호자가 말한 내용을 정확하게 텍스트로 전사하세요. "
                "설명, 요약, 답변, 따옴표는 추가하지 말고 실제 발화만 출력하세요. "
                "한국어 음성이면 한국어 그대로 작성하세요."
            ),
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav",
            ),
        ],
    )

    if not response.text:
        raise RuntimeError("음성을 텍스트로 변환하지 못했습니다.")

    return response.text.strip()


def build_ai_history():
    contents = []
    for message in ss.ai_messages:
        contents.append(
            types.Content(
                role=message["role"],
                parts=[types.Part.from_text(text=message["content"])],
            )
        )
    return contents


def generate_care_answer(question: str, model_name: str) -> str:
    client = gemini_client()

    system_instruction = f"""
당신은 '일어나 파트라슈' 앱 안의 반려견 케어 안내 AI입니다.
보호자가 시니어 강아지를 일상에서 돌볼 때 이해하기 쉬운 한국어로 설명하세요.

현재 앱에 저장된 참고 기록:
{latest_dog_context()}

답변 원칙:
1. 위 기록은 사용자가 앱에 직접 입력한 참고 정보이므로 질문과 관련 있을 때만 활용하세요.
2. 질환을 확정 진단하거나 처방·약 용량 변경을 지시하지 마세요.
3. 응급 가능성이 있거나 증상이 지속·악화된다고 사용자가 말하면 동물병원 진료를 권하세요.
4. 복약 질문에서는 수의사가 처방한 약의 임의 중단·변경을 권하지 마세요.
5. 특별히 긴 설명을 요청하지 않으면 2~5문장 정도로 간결하게 답하세요.
6. 음성으로 들었을 때 자연스럽게 작성하고 복잡한 표나 마크다운은 피하세요.
7. 이전 대화의 맥락을 이어서 답하세요.
"""

    contents = build_ai_history()
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=question)],
        )
    )

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        ),
    )

    if not response.text:
        raise RuntimeError("AI 답변을 생성하지 못했습니다.")

    return response.text.strip()


def create_tts_audio(text: str) -> bytes:
    buffer = BytesIO()
    gTTS(text=text, lang="ko").write_to_fp(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def reset_ai_conversation():
    ss.ai_chat = []
    ss.ai_messages = []
    ss.ai_processed_signature = None
    ss.ai_answer_audio = None
    ss.ai_error = None


# ============================================================
# 이미지 경로
# ============================================================

PHOTO_GOOD = PHOTO_DIR / "main2.png"
PHOTO_WATCH = PHOTO_DIR / "main.png"
PHOTO_WORRIED = PHOTO_DIR / "main3.png"


# ============================================================
# 사이드바
# ============================================================

with st.sidebar:
    st.markdown("### 🐾 파트라슈 프로필")

    ss.dog_name = st.text_input("이름", value=ss.dog_name)
    ss.dog_age = st.slider("나이 (세)", 0, 20, ss.dog_age)
    ss.dog_breed = st.selectbox(
        "견종",
        BREEDS,
        index=BREEDS.index(ss.dog_breed) if ss.dog_breed in BREEDS else 0,
    )

    stage = senior_stage(ss.dog_age)
    st.markdown(f"**현재 단계:** {stage}")
    st.caption("※ 나이 단계는 데모용 단순 참고 구분입니다.")

    st.divider()
    st.caption("파트라슈 추천")

    for ad_name in ["ad1.png", "ad2.png", "ad3.png"]:
        ad_path = PHOTO_DIR / ad_name
        if ad_path.exists():
            st.image(str(ad_path), use_container_width=True)

    # AI 파트라슈와 대화 설정은 광고/추천 이미지 3개 아래, 사이드바 최하단에 배치
    st.divider()
    st.markdown("### 🤖 AI 파트라슈와 대화 설정")
    selected_model_label = st.radio(
        "Gemini 모델",
        list(MODEL_OPTIONS.keys()),
        index=0,
    )
    selected_model = MODEL_OPTIONS[selected_model_label]

    if st.button("AI 파트라슈와 대화 대화 초기화", use_container_width=True):
        reset_ai_conversation()
        st.toast("AI 파트라슈와 대화를 초기화했어요.")


# ============================================================
# 메인 타이틀 + 대표 이미지
# ============================================================

st.markdown('<div class="main-title">일어나 파트라슈</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="main-sub">'
    f'{ss.dog_name}({ss.dog_age}세)야, 오늘도 같이 건강 체크하자! '
    f'이제 궁금한 건 말로 물어봐도 돼요. 🐾'
    f'</div>',
    unsafe_allow_html=True,
)

photo_col, content_col = st.columns([1, 2.45])

with photo_col:
    if ss.health_history:
        latest_verdict = ss.health_history[-1]["판정"]
        if "양호" in latest_verdict:
            current_photo = PHOTO_GOOD
        elif "관찰" in latest_verdict:
            current_photo = PHOTO_WATCH
        else:
            current_photo = PHOTO_WORRIED
    else:
        if ss.dog_age >= 11:
            current_photo = PHOTO_WORRIED
        elif ss.dog_age >= 7:
            current_photo = PHOTO_WATCH
        else:
            current_photo = PHOTO_GOOD

    safe_image(current_photo)


# ============================================================
# 탭
# ============================================================

with content_col:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "⚖️ 체중관리",
            "🩺 건강체크",
            "💊 복약알리미",
            "📔 케어기록",
            "🤖 AI 파트라슈와 대화",
        ]
    )

    # --------------------------------------------------------
    # 1. 체중관리
    # --------------------------------------------------------
    with tab1:
        st.subheader("오늘의 체중을 기록해주세요")

        col1, col2 = st.columns([2, 1])

        with col1:
            weight = st.number_input(
                "체중 (kg)",
                min_value=0.0,
                max_value=80.0,
                value=5.0,
                step=0.1,
            )

        with col2:
            st.write("")
            st.write("")
            if st.button("기록하기 📝", use_container_width=True, key="save_weight"):
                ss.weight_log.append(
                    {
                        "날짜": date.today().isoformat(),
                        "체중": float(weight),
                    }
                )
                st.toast(f"{ss.dog_name}의 체중 {weight}kg가 기록되었어요!")

        if ss.weight_log:
            df = pd.DataFrame(ss.weight_log).copy()
            df["회차"] = [f"{i + 1}회" for i in range(len(df))]

            chart = (
                alt.Chart(df)
                .mark_line(point=True, color="#FF8C69", strokeWidth=3)
                .encode(
                    x=alt.X("회차:O", title="기록 순서", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y(
                        "체중:Q",
                        title="체중 (kg)",
                        scale=alt.Scale(zero=False),
                    ),
                    tooltip=["회차", "체중", "날짜"],
                )
                .properties(height=280)
            )
            st.altair_chart(chart, use_container_width=True)
            st.caption(f"지금까지 {len(ss.weight_log)}번 기록했어요.")
        else:
            st.info("아직 기록이 없어요. 첫 체중을 기록해보세요!")

        st.caption(
            "🐾 체중의 의미는 체격·견종·질환 등에 따라 달라질 수 있으므로 "
            "급격한 변화가 걱정되면 동물병원과 상담해주세요."
        )

    # --------------------------------------------------------
    # 2. 건강체크
    # --------------------------------------------------------
    with tab2:
        st.subheader("시니어 건강 체크리스트")
        st.caption("최근 1주일 기준으로 체크해주세요. 점수가 낮을수록 양호한 데모 지표입니다.")

        answers = [
            st.radio(
                "계단/산책 시 머뭇거리거나 힘들어하나요?",
                ["전혀 아니다", "가끔 그렇다", "자주 그렇다"],
                horizontal=True,
                key="health_q1",
            ),
            st.radio(
                "최근 식욕이 줄었나요?",
                ["전혀 아니다", "가끔 그렇다", "자주 그렇다"],
                horizontal=True,
                key="health_q2",
            ),
            st.radio(
                "평소보다 잠을 많이 자거나 활동량이 줄었나요?",
                ["전혀 아니다", "가끔 그렇다", "자주 그렇다"],
                horizontal=True,
                key="health_q3",
            ),
            st.radio(
                "배변/배뇨에 평소와 다른 점이 있나요?",
                ["전혀 아니다", "가끔 그렇다", "자주 그렇다"],
                horizontal=True,
                key="health_q4",
            ),
        ]

        score_map = {
            "전혀 아니다": 0,
            "가끔 그렇다": 1,
            "자주 그렇다": 2,
        }

        if st.button("결과 확인하기 🔍", use_container_width=True, key="health_submit"):
            total = sum(score_map[x] for x in answers)

            if total <= 2:
                verdict = "양호 🟢"
            elif total <= 5:
                verdict = "관찰 필요 🟡"
            else:
                verdict = "병원 상담 권장 🔴"

            ss.health_history.append(
                {
                    "날짜": date.today().isoformat(),
                    "점수": total,
                    "판정": verdict,
                }
            )
            st.toast(f"점수 {total}점 — {verdict}")
            st.rerun()

        if ss.health_history:
            latest = ss.health_history[-1]
            st.divider()

            if "양호" in latest["판정"]:
                st.success(
                    f"점수 {latest['점수']}점 — 현재 체크 결과는 양호 범위예요."
                )
            elif "관찰" in latest["판정"]:
                st.warning(
                    f"점수 {latest['점수']}점 — 변화를 며칠 더 관찰해보세요."
                )
            else:
                st.error(
                    f"점수 {latest['점수']}점 — 증상이 지속된다면 동물병원 상담을 권장해요."
                )

            st.caption("📋 최근 체크 기록")
            for h in reversed(ss.health_history[-5:]):
                st.write(f"- {h['날짜']} · {h['점수']}점 · {h['판정']}")

        st.caption(
            "⚠️ 이 체크리스트는 데모용 참고 도구이며 수의사의 진단을 대신하지 않습니다."
        )

    # --------------------------------------------------------
    # 3. 복약알리미
    # --------------------------------------------------------
    with tab3:
        st.subheader("복약 등록 및 체크")

        with st.expander("➕ 새 약 등록하기"):
            med_name = st.text_input(
                "약 이름",
                placeholder="예: 관절영양제",
                key="med_name",
            )
            med_time = st.selectbox(
                "복용 시간",
                ["아침", "점심", "저녁", "취침전"],
                key="med_time",
            )

            if st.button("약 추가하기", key="add_med"):
                if med_name.strip():
                    ss.medicines.append(
                        {
                            "이름": med_name.strip(),
                            "시간": med_time,
                        }
                    )
                    st.toast(f"'{med_name}' 등록 완료!")
                else:
                    st.warning("약 이름을 입력해주세요.")

        st.divider()
        st.caption("✅ 오늘 복용 체크")

        if not ss.medicines:
            st.info("등록된 약이 없어요.")
        else:
            for i, med in enumerate(ss.medicines):
                med_key = f"{med['이름']}_{med['시간']}_{i}"

                checked = st.checkbox(
                    f"{med['시간']} — {med['이름']}",
                    value=ss.med_check_today.get(med_key, False),
                    key=f"med_check_{i}",
                )

                if checked and not ss.med_check_today.get(med_key, False):
                    st.toast(f"{med['이름']} 복용 완료! 🎉")

                ss.med_check_today[med_key] = checked

            done = sum(
                1
                for i, med in enumerate(ss.medicines)
                if ss.med_check_today.get(f"{med['이름']}_{med['시간']}_{i}", False)
            )

            st.progress(done / len(ss.medicines))
            st.caption(f"오늘 {done} / {len(ss.medicines)}개 복용 완료")

        st.caption(
            "💊 처방약의 용량·횟수 변경이나 중단은 반드시 담당 수의사와 상의해주세요."
        )

    # --------------------------------------------------------
    # 4. 케어기록
    # --------------------------------------------------------
    with tab4:
        st.subheader("오늘의 케어 일기")

        walk_min = st.slider(
            "오늘 산책 시간 (분)",
            0,
            120,
            20,
            key="walk_min",
        )

        memo = st.text_area(
            "한줄 메모",
            placeholder="예: 오늘은 평소보다 더 활발했어요 🐕",
            key="care_memo",
        )

        if st.button(
            "오늘 기록 저장하기 💾",
            use_container_width=True,
            key="save_care",
        ):
            ss.care_log.append(
                {
                    "날짜": date.today().isoformat(),
                    "산책분": walk_min,
                    "메모": memo.strip() if memo.strip() else "(메모 없음)",
                }
            )
            st.toast("오늘의 기록이 저장되었어요!")

        if ss.care_log:
            st.divider()
            st.caption("📔 최근 케어 기록")
            for log in reversed(ss.care_log[-5:]):
                st.markdown(
                    f"**{log['날짜']}** · 🚶 산책 {log['산책분']}분  \n"
                    f"💬 {log['메모']}"
                )
                st.markdown("---")
        else:
            st.info("아직 기록이 없어요. 오늘 하루를 기록해보세요!")

    # --------------------------------------------------------
    # 5. AI 음성 파트라슈
    # --------------------------------------------------------
    with tab5:
        st.markdown(
            """
            <div class="ai-hero">
                <div class="ai-kicker">VOICE · AI · SENIOR CARE</div>
                <div class="ai-title">🐶 AI 파트라슈와 대화에게 말해보세요</div>
                <div class="ai-desc">
                    보호자가 질문하면 음성을 글로 바꾸고,
                    현재 앱에 기록된 프로필·체중·건강체크·복약·케어기록을 참고해
                    일상 케어 정보를 설명합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not GEMINI_API_KEY:
            st.warning(
                "파트라슈 음성 기능을 사용하려면 Streamlit Cloud의 "
                "App settings → Secrets에 Gemini API Key를 등록해야 합니다."
            )

        context_cols = st.columns(3)
        context_cols[0].metric("나이", f"{ss.dog_age}세")
        context_cols[1].metric(
            "최근 체중",
            f"{ss.weight_log[-1]['체중']}kg" if ss.weight_log else "-",
        )
        context_cols[2].metric(
            "건강체크",
            ss.health_history[-1]["판정"].replace("🟢", "").replace("🟡", "").replace("🔴", "").strip()
            if ss.health_history
            else "-",
        )

        st.caption(f"현재 AI 모델: {selected_model_label}")

        audio_value = st.audio_input(
            f"{ss.dog_name}에 대해 궁금한 점을 말해 주세요",
            sample_rate=16000,
            key="patrasche_voice_input",
        )

        if audio_value is not None:
            audio_bytes = audio_value.getvalue()
            audio_hash = hashlib.sha256(audio_bytes).hexdigest()
            signature = f"{audio_hash}|{selected_model}"

            if ss.ai_processed_signature != signature:
                ss.ai_error = None
                ss.ai_answer_audio = None

                try:
                    with st.status(
                        "파트라슈의 기록을 확인하고 있어요...",
                        expanded=True,
                    ) as status:
                        st.write("① 음성을 텍스트로 변환 중...")
                        question = transcribe_audio(
                            audio_bytes,
                            selected_model,
                        )

                        st.write("② 기록과 질문을 함께 살펴보는 중...")
                        answer = generate_care_answer(
                            question,
                            selected_model,
                        )

                        ss.ai_chat.extend(
                            [
                                {"role": "user", "content": question},
                                {"role": "assistant", "content": answer},
                            ]
                        )

                        ss.ai_messages.extend(
                            [
                                {"role": "user", "content": question},
                                {"role": "model", "content": answer},
                            ]
                        )

                        st.write("③ 답변을 음성으로 준비 중...")
                        try:
                            ss.ai_answer_audio = create_tts_audio(answer)
                        except Exception as tts_error:
                            ss.ai_answer_audio = None
                            st.write(
                                f"음성 재생 생성은 건너뛰었습니다: {tts_error}"
                            )

                        ss.ai_processed_signature = signature

                        status.update(
                            label="답변이 준비됐어요!",
                            state="complete",
                            expanded=False,
                        )

                except Exception as e:
                    ss.ai_error = str(e)
                    ss.ai_processed_signature = signature

        if ss.ai_error:
            st.error(f"AI 처리 중 오류가 발생했습니다: {ss.ai_error}")

        st.markdown("#### 💬 AI 파트라슈와 대화와의 대화")

        if not ss.ai_chat:
            st.info(
                "아직 AI 대화가 없어요. "
                "예: “파트라슈가 요즘 산책할 때 자꾸 멈추는데 뭘 기록해두면 좋을까?”"
            )
        else:
            for message in ss.ai_chat:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        if ss.ai_answer_audio:
            st.markdown("#### 🔊 최근 음성 답변")
            st.audio(
                ss.ai_answer_audio,
                format="audio/mpeg",
                autoplay=True,
            )

        st.markdown(
            """
            <div class="medical-note">
                ※ AI 파트라슈와 대화는 일반적인 반려견 돌봄 정보를 제공하는 데모 기능입니다.
                진단·처방을 대신하지 않으며, 상태가 급격히 나빠지거나 걱정되는 증상이 지속되면
                동물병원에 문의하세요.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 하단 광고 배너
# ============================================================

AD4_PATH = PHOTO_DIR / "ad4.png"
AD5_PATH = PHOTO_DIR / "ad5.png"

COUPANG_URL = (
    "https://www.coupang.com/np/search?"
    "component=&q=%EC%95%A0%EA%B2%AC%EC%9A%A9%ED%92%88&channel=user"
)

if AD4_PATH.exists() and AD5_PATH.exists():
    ad4_b64 = base64.b64encode(AD4_PATH.read_bytes()).decode()
    ad5_b64 = base64.b64encode(AD5_PATH.read_bytes()).decode()

    banner_html = f"""
    <html>
    <body style="margin:0; padding:0; background:transparent;">
      <a href="{COUPANG_URL}" target="_blank" style="display:block;">
        <img id="ad-banner-slide"
             src="data:image/png;base64,{ad4_b64}"
             style="width:100%; height:auto; display:block; border-radius:12px;">
      </a>
      <script>
        const imgs = [
            "data:image/png;base64,{ad4_b64}",
            "data:image/png;base64,{ad5_b64}"
        ];
        let idx = 0;
        setInterval(function() {{
            idx = (idx + 1) % imgs.length;
            const el = document.getElementById("ad-banner-slide");
            if (el) el.src = imgs[idx];
        }}, 5000);
      </script>
    </body>
    </html>
    """
    components.html(banner_html, height=360, scrolling=False)


# ============================================================
# 공통 고지
# ============================================================

st.markdown("---")
st.caption(
    "🐾 일어나 파트라슈는 반려견 건강 기록과 일상 케어를 돕는 데모 앱입니다. "
    "의학적 진단이나 수의사의 진료를 대체하지 않습니다."
)
