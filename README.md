# 🐕 일어나 파트라슈

노견 보호자를 위한 강아지 건강 모니터링 미니 앱입니다.
강아지의 체중 변화, 건강 상태, 복약 여부, 일상 케어 기록을 한 화면에서 관리할 수 있도록 구성했습니다.

---

## 🔗 배포 링크

Streamlit Community Cloud를 통해 배포한 앱입니다.

```text
https://patrasche-senior-care.streamlit.app
```

---

## 🧭 프로젝트 개요

`일어나 파트라슈`는 시니어 강아지 보호자가 반려견의 일상 건강 상태를 간단하게 기록하고 확인할 수 있도록 만든 Streamlit 기반 웹 앱입니다.

주요 목적은 다음과 같습니다.

* 체중 변화 기록
* 시니어 건강 체크
* 복약 여부 관리
* 산책 및 케어 메모 기록
* 보호자 중심의 간단한 건강 모니터링

---

## 🛠️ 실행 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 앱 실행

```bash
streamlit run app.py
```

로컬 환경에서 `streamlit` 명령어가 바로 실행되지 않는 경우 아래 명령어를 사용할 수 있습니다.

```bash
py -m streamlit run app.py
```

---

## ✨ 주요 기능

### 🐾 사이드바 프로필

강아지의 이름, 나이, 견종을 입력하면 나이에 따라 시니어 단계를 자동으로 표시합니다.

* 성인기
* 시니어 진입
* 노령기

### ⚖️ 체중관리

강아지의 체중을 입력하면 기록이 누적되고, 체중 변화 추이를 그래프로 확인할 수 있습니다.

### 🩺 건강체크

시니어 강아지의 건강 상태를 확인하기 위한 4문항 체크리스트를 제공합니다.
응답 결과에 따라 다음과 같이 상태를 구분합니다.

* 양호
* 관찰 필요
* 병원 상담 권장

### 💊 복약알리미

약 이름과 복용 시간을 등록하고, 오늘 복용 여부를 체크할 수 있습니다.
복용 완료 비율은 진행률로 표시됩니다.

### 📔 케어기록

오늘의 산책 시간과 한줄 메모를 저장하여 최근 케어 기록을 확인할 수 있습니다.

### 📢 광고 배너

앱의 사이드바와 하단 영역에 강아지 관련 광고 이미지를 배치했습니다.

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

## 🧩 사용 기술

* Python
* Streamlit
* Pandas
* Altair
* Session State
* HTML / CSS

---

## ✅ 충족 요소 체크

| 구분     | 내용                                                                              |
| ------ | ------------------------------------------------------------------------------- |
| 위젯     | text_input, slider, selectbox, number_input, button, radio, checkbox, text_area |
| 레이아웃   | sidebar, tabs, columns                                                          |
| 상태 관리  | st.session_state 활용                                                             |
| 시각화    | 체중 변화 추이 그래프                                                                    |
| 꾸미기 요소 | 이모지, 색상 테마, 이미지 광고, toast 메시지, progress bar                                     |
| 배포     | GitHub + Streamlit Community Cloud                                              |

---

## ⚠️ 주의사항

이 앱은 데모용 참고 도구이며, 의학적 진단을 대체하지 않습니다.
강아지의 건강 이상이 의심될 경우 반드시 동물병원과 상담해야 합니다.
