# 🐕 일어나 파트라슈

노견 보호자를 위한 **강아지 건강 기록 + AI 음성 케어비서** 통합 앱입니다.

기존의 체중관리, 건강체크, 복약알리미, 케어기록 기능에
Gemini 기반 음성 질문·답변 기능을 추가했습니다.

---

## 🔗 배포

Streamlit Community Cloud를 사용합니다.

```text
https://patrasche-senior-care.streamlit.app
```

---

## ✨ 주요 기능

### 🐾 반려견 프로필
이름, 나이, 견종을 등록하고 데모 기준의 시니어 단계를 표시합니다.

### ⚖️ 체중관리
체중 기록을 누적하고 Altair 그래프로 추이를 확인합니다.

### 🩺 건강체크
시니어 강아지 일상 상태를 4문항으로 기록하고
`양호 / 관찰 필요 / 병원 상담 권장`의 데모 상태로 구분합니다.

### 💊 복약알리미
약 이름과 시간을 등록하고 당일 복용 여부를 체크합니다.

### 📔 케어기록
산책 시간과 한 줄 메모를 기록합니다.

### 🎙️ AI 케어비서
마이크로 질문하면 아래 순서로 동작합니다.

```text
음성 질문
→ Gemini 음성→텍스트
→ 현재 반려견 프로필·기록 문맥과 함께 AI 답변 생성
→ gTTS 음성 답변
→ 대화 기록 유지
```

AI는 현재 앱에 입력된 다음 정보를 질문과 관련 있을 때 참고합니다.

- 반려견 이름 / 나이 / 견종
- 최근 체중
- 최근 건강체크
- 등록 복약
- 최근 산책 및 케어 메모

### 🤖 Gemini 모델 선택

사이드바에서 선택할 수 있습니다.

- Gemini 3.6 Flash
- Gemini 3.5 Flash-Lite

---

## 🔐 Gemini API Key

실제 API Key는 GitHub에 올리지 않습니다.

Streamlit Community Cloud에서:

```text
Manage app
→ Settings
→ Secrets
```

아래 형식으로 등록합니다.

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

---

## 📁 프로젝트 구조

```text
patrasche-senior-care/
├─ app.py
├─ requirements.txt
├─ README.md
└─ files/
   └─ photo/
      ├─ ad1.png
      ├─ ad2.png
      ├─ ad3.png
      ├─ ad4.png
      ├─ ad5.png
      ├─ main.png
      ├─ main2.png
      └─ main3.png
```

---

## 🛠️ 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Windows에서 `streamlit` 명령이 바로 실행되지 않으면:

```bash
py -m streamlit run app.py
```

---

## ⚠️ 주의사항

이 앱은 데모용 참고 도구이며 수의사의 진단·처방을 대체하지 않습니다.
강아지의 상태가 급격히 나빠지거나 이상 증상이 지속되면 동물병원과 상담하세요.
