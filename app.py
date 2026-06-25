"""
일어나 파트라슈
노견(시니어 강아지) 보호자를 위한 건강 모니터링 미니 앱

구성:
- 체중관리 : 체중 기록 누적 + 추이 그래프 (입력 순서 기준, 변화 잘 보이는 Y축)
- 건강체크 : 시니어 건강 체크리스트 → 점수 판정
- 복약알리미 : 약 등록 + 오늘 복용 체크
- 케어기록 : 산책시간 + 한줄메모 일기

실행: streamlit run app.py
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import base64
from datetime import date
from pathlib import Path

# ============================================================
# 페이지 설정 + 색감 테마 (살구·코랄 톤)
# ============================================================
st.set_page_config(page_title="일어나 파트라슈", page_icon="🐕", layout="wide")

CUSTOM_CSS = """
<style>
    /* 전체 배경 - 크림 살구색 */
    .stApp {
        background-color: #FFF6EE;
    }

    /* 메인 타이틀 */
    .main-title {
        color: #4A3B32;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .main-sub {
        color: #B5705A;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }

    /* 사이드바 배경 */
    section[data-testid="stSidebar"] {
        background-color: #FFEADC;
    }

    /* 버튼 - 코랄톤 */
    .stButton > button {
        background-color: #FF8C69;
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #FF7A52;
        color: white;
    }

    /* 탭 디자인 - 더 길고 넓게 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFE3D3;
        border-radius: 10px 10px 0 0;
        color: #4A3B32;
        font-weight: 600;
        padding: 10px 28px;
        min-width: 160px;
        justify-content: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF8C69 !important;
        color: white !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# matplotlib 한글 폰트 설정 (Windows 환경 기준)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# session_state 초기화 (앱의 '기억' 저장소)
# ============================================================
def init_state():
    defaults = {
        "dog_name": "파트라슈",
        "dog_age": 8,
        "dog_breed": "믹스견",
        "weight_log": [],      # [{"체중":...}, ...]
        "health_history": [],  # [{"날짜":..., "점수":..., "판정":...}, ...]
        "medicines": [],       # [{"이름":..., "시간":...}, ...]
        "med_check_today": {},  # {"약이름": True/False}
        "care_log": [],        # [{"날짜":..., "산책분":..., "메모":...}, ...]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()
ss = st.session_state

# 사진 경로 — 나이/건강체크 상태에 따라 전환 (3종)
BASE_DIR = Path(__file__).parent
PHOTO_DIR = BASE_DIR / "files" / "photo"

PHOTO_GOOD = PHOTO_DIR / "main2.png"
PHOTO_WATCH = PHOTO_DIR / "main.png"
PHOTO_WORRIED = PHOTO_DIR / "main3.png"


# ============================================================
# 사이드바 — 파트라슈 프로필 (전체 화면 공통)
# ============================================================
with st.sidebar:
    st.markdown("### 🐾 파트라슈 프로필")
    ss.dog_name = st.text_input("이름", value=ss.dog_name)
    ss.dog_age = st.slider("나이 (세)", 0, 20, ss.dog_age)
    ss.dog_breed = st.selectbox(
        "견종", ["믹스견", "말티즈", "푸들", "시바견", "진돗개", "기타"],
        index=["믹스견", "말티즈", "푸들", "시바견", "진돗개", "기타"].index(ss.dog_breed)
        if ss.dog_breed in ["믹스견", "말티즈", "푸들", "시바견", "진돗개", "기타"] else 0,
    )

    # 시니어 단계 자동 판정 (간단 로직)
    if ss.dog_age >= 11:
        stage = "🟠 노령기"
    elif ss.dog_age >= 7:
        stage = "🟡 시니어 진입"
    else:
        stage = "🟢 성인기"
    st.markdown(f"**현재 단계:** {stage}")
    st.caption("※ 소형견 기준 단순 참고용 구분이에요")

    # 광고 영역
    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    AD_DIR = PHOTO_DIR
    st.image(str(AD_DIR / "ad1.png"), use_container_width=True)
    st.image(str(AD_DIR / "ad2.png"), use_container_width=True)
    st.image(str(AD_DIR / "ad3.png"), use_container_width=True)


# ============================================================
# 메인 타이틀
# ============================================================
st.markdown('<div class="main-title">일어나 파트라슈</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="main-sub">{ss.dog_name}({ss.dog_age}세)야, 오늘도 같이 건강 체크하자! 🐾</div>',
    unsafe_allow_html=True,
)

# ============================================================
# 본문 레이아웃 — 좌측 큰 사진 + 우측 탭 콘텐츠
# ============================================================
photo_col, content_col = st.columns([1, 2.2])

with photo_col:
    # 사진 결정: 건강체크 결과가 최우선, 기록이 없으면 나이 3단계 기준
    if ss.health_history:
        latest_verdict = ss.health_history[-1]["판정"]
        if "양호" in latest_verdict:
            current_photo = PHOTO_GOOD
        elif "관찰" in latest_verdict:
            current_photo = PHOTO_WATCH
        else:  # 병원 상담 권장
            current_photo = PHOTO_WORRIED
    else:
        if ss.dog_age >= 11:
            current_photo = PHOTO_WORRIED   # 노령기
        elif ss.dog_age >= 7:
            current_photo = PHOTO_WATCH     # 시니어 진입
        else:
            current_photo = PHOTO_GOOD      # 성인기

    st.image(current_photo, use_container_width=True)

with content_col:
    # --------------------------------------------------------
    # 탭 구성 (레이아웃 요소)
    # --------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["⚖️ 체중관리", "🩺 건강체크", "💊 복약알리미", "📔 케어기록"])

    # ----------------------------------------------------
    # 탭 1. 체중관리
    # ----------------------------------------------------
    with tab1:
        st.subheader("오늘의 체중을 기록해주세요")

        col1, col2 = st.columns([2, 1])
        with col1:
            weight = st.number_input("체중 (kg)", min_value=0.0, max_value=50.0, value=5.0, step=0.1)
        with col2:
            st.write("")
            st.write("")
            if st.button("기록하기 📝", use_container_width=True):
                ss.weight_log.append({"체중": weight})
                st.toast(f"{ss.dog_name}의 체중 {weight}kg가 기록되었어요!")

        if ss.weight_log:
            df = pd.DataFrame(ss.weight_log)
            x_labels = [f"{i+1}회차" for i in range(len(df))]

            # Y축 스케일 보정: 소형견은 0.1~0.2kg 단위 변화라 범위를 좁혀서 변화가 보이게
            min_w, max_w = df["체중"].min(), df["체중"].max()
            spread = max_w - min_w
            padding = 0.5 if spread < 1.0 else spread * 0.15
            y_min = max(0, min_w - padding)
            y_max = max_w + padding if max_w + padding > y_min else y_min + 1

            fig, ax = plt.subplots(figsize=(6, 3))
            fig.patch.set_alpha(0)
            ax.set_facecolor("none")
            ax.plot(x_labels, df["체중"], marker="o", color="#FF8C69", linewidth=2)
            ax.set_ylim(y_min, y_max)
            ax.set_ylabel("체중 (kg)")
            ax.tick_params(axis="x", rotation=0)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="y", alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)

            st.caption(f"지금까지 {len(ss.weight_log)}번 기록했어요. (가로축: 입력 순서)")
        else:
            st.info("아직 기록이 없어요. 첫 체중을 기록해보세요!")

        st.divider()
        st.caption("🐾 이 앱은 참고용 데모이며, 의학적 진단을 대체하지 않습니다. 건강이 걱정되면 동물병원과 상담해주세요.")

    # ----------------------------------------------------
    # 탭 2. 건강체크 (시니어 체크리스트)
    # ----------------------------------------------------
    with tab2:
        st.subheader("시니어 건강 체크리스트")
        st.caption("최근 1주일 기준으로 체크해주세요. (점수가 낮을수록 좋아요)")

        q1 = st.radio("계단/산책 시 머뭇거리거나 힘들어하나요?",
                      ["전혀 아니다", "가끔 그렇다", "자주 그렇다"], horizontal=True)
        q2 = st.radio("최근 식욕이 줄었나요?",
                      ["전혀 아니다", "가끔 그렇다", "자주 그렇다"], horizontal=True)
        q3 = st.radio("평소보다 잠을 많이 자거나 활동량이 줄었나요?",
                      ["전혀 아니다", "가끔 그렇다", "자주 그렇다"], horizontal=True)
        q4 = st.radio("배변/배뇨에 평소와 다른 점이 있나요?",
                      ["전혀 아니다", "가끔 그렇다", "자주 그렇다"], horizontal=True)

        score_map = {"전혀 아니다": 0, "가끔 그렇다": 1, "자주 그렇다": 2}

        if st.button("결과 확인하기 🔍", use_container_width=True):
            total = score_map[q1] + score_map[q2] + score_map[q3] + score_map[q4]

            if total <= 2:
                verdict = "양호 🟢"
            elif total <= 5:
                verdict = "관찰 필요 🟡"
            else:
                verdict = "병원 상담 권장 🔴"

            ss.health_history.append({"날짜": date.today().isoformat(), "점수": total, "판정": verdict})
            st.toast(f"점수 {total}점 — {verdict}")
            st.rerun()

        if ss.health_history:
            st.divider()
            latest = ss.health_history[-1]
            if "양호" in latest["판정"]:
                st.success(f"점수 {latest['점수']}점 — {ss.dog_name}는 양호한 상태예요! 😊")
            elif "관찰" in latest["판정"]:
                st.warning(f"점수 {latest['점수']}점 — 며칠 더 관찰이 필요해요. 변화가 계속되면 병원 상담을 권장해요.")
            else:
                st.error(f"점수 {latest['점수']}점 — 가까운 병원에서 상담을 받아보시는 게 좋겠어요.")

            st.caption("📋 체크 기록")
            for h in reversed(ss.health_history[-5:]):
                st.write(f"- {h['날짜']} · {h['점수']}점 · {h['판정']}")

        st.divider()
        st.caption("🐾 이 앱은 참고용 데모이며, 의학적 진단을 대체하지 않습니다. 건강이 걱정되면 동물병원과 상담해주세요.")

    # ----------------------------------------------------
    # 탭 3. 복약알리미
    # ----------------------------------------------------
    with tab3:
        st.subheader("복약 등록 및 체크")

        with st.expander("➕ 새 약 등록하기"):
            med_name = st.text_input("약 이름", placeholder="예: 관절영양제")
            med_time = st.selectbox("복용 시간", ["아침", "점심", "저녁", "취침전"])
            if st.button("약 추가하기"):
                if med_name.strip():
                    ss.medicines.append({"이름": med_name.strip(), "시간": med_time})
                    st.toast(f"'{med_name}' 등록 완료!")
                else:
                    st.warning("약 이름을 입력해주세요.")

        st.divider()
        st.caption("✅ 오늘 복용 체크")

        if not ss.medicines:
            st.info("등록된 약이 없어요. 위에서 먼저 등록해주세요.")
        else:
            for i, med in enumerate(ss.medicines):
                key = f"{med['이름']}_{med['시간']}"
                checked = st.checkbox(
                    f"{med['시간']} — {med['이름']}", value=ss.med_check_today.get(key, False), key=f"med_{i}"
                )
                if checked and not ss.med_check_today.get(key, False):
                    st.toast(f"{med['이름']} 복용 완료! 잘했어요 🎉")
                ss.med_check_today[key] = checked

            done = sum(ss.med_check_today.values())
            st.progress(done / len(ss.medicines) if ss.medicines else 0)
            st.caption(f"오늘 {done} / {len(ss.medicines)}개 복용 완료")

        st.divider()
        st.caption("🐾 이 앱은 참고용 데모이며, 의학적 진단을 대체하지 않습니다. 건강이 걱정되면 동물병원과 상담해주세요.")

    # ----------------------------------------------------
    # 탭 4. 케어기록
    # ----------------------------------------------------
    with tab4:
        st.subheader("오늘의 케어 일기")

        walk_min = st.slider("오늘 산책 시간 (분)", 0, 120, 20)
        memo = st.text_area("한줄 메모", placeholder="예: 오늘은 평소보다 더 활발했어요 🐕")

        if st.button("오늘 기록 저장하기 💾", use_container_width=True):
            ss.care_log.append({
                "날짜": date.today().isoformat(),
                "산책분": walk_min,
                "메모": memo.strip() if memo.strip() else "(메모 없음)",
            })
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

        st.divider()
        st.caption("🐾 이 앱은 참고용 데모이며, 의학적 진단을 대체하지 않습니다. 건강이 걱정되면 동물병원과 상담해주세요.")


# ============================================================
# 하단 배너 광고 (ad4 ↔ ad5, 5초마다 자동 전환)
# ============================================================
AD4_PATH = PHOTO_DIR / "ad4.png"
AD5_PATH = PHOTO_DIR / "ad5.png"
COUPANG_URL = "https://www.coupang.com/np/search?component=&q=%EC%95%A0%EA%B2%AC%EC%9A%A9%ED%92%88&traceId=mqsxbagw&channel=user"

try:
    with open(AD4_PATH, "rb") as f:
        ad4_b64 = base64.b64encode(f.read()).decode()
    with open(AD5_PATH, "rb") as f:
        ad5_b64 = base64.b64encode(f.read()).decode()

    banner_html = f"""
    <html>
    <body style="margin:0; padding:0;">
      <a href="{COUPANG_URL}" target="_blank" style="display:block;">
        <img id="ad-banner-slide" src="data:image/png;base64,{ad4_b64}"
             style="width:100%; height:auto; display:block; border-radius:8px;">
      </a>
      <script>
        const imgs = [
            "data:image/png;base64,{ad4_b64}",
            "data:image/png;base64,{ad5_b64}"
        ];
        let idx = 0;
        setInterval(function() {{
            idx = (idx + 1) % imgs.length;
            document.getElementById("ad-banner-slide").src = imgs[idx];
        }}, 5000);
      </script>
    </body>
    </html>
    """
    components.html(banner_html, height=400, scrolling=False)
except FileNotFoundError as e:
    st.caption(f"(광고 이미지를 찾을 수 없어요: {e.filename})")
