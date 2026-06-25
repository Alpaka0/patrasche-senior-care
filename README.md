# 🐕 우리 댕댕이 시니어케어

노견(시니어 강아지) 보호자를 위한 건강 모니터링 미니 앱입니다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 구성

- **사이드바**: 강아지 이름·나이·견종 입력 → 시니어 단계 자동 표시
- **⚖️ 체중관리**: 체중 입력 → 기록 누적 → 추이 그래프
- **🩺 건강체크**: 시니어 건강 체크리스트(4문항) → 점수 합산 → 양호/관찰필요/병원상담 판정
- **💊 복약알리미**: 약 등록 → 오늘 복용 체크 → 진행률 표시
- **📔 케어기록**: 산책시간 + 한줄메모 일기 누적

## 충족 요소 체크

- ✅ 위젯 2개 이상: number_input, button, radio, selectbox, checkbox, slider, text_area, text_input 등
- ✅ 레이아웃 1개 이상: sidebar + tabs + columns
- ✅ session_state 활용: weight_log, health_history, medicines, med_check_today, care_log
- ✅ 꾸미기 요소: 이모지, balloons(), 색상 메시지(success/warning/error), progress bar

## 다음 단계 (꾸미기 / 배포)

1. **꾸미기 단계**: 색감 통일, 강아지 캐릭터 이미지, 추가 이모지, 카드형 UI 등
2. **GitHub 배포**: 코드 + requirements.txt를 GitHub repo에 올리고 Streamlit Community Cloud에서 연결하면 배포 가능

## 주의

이 앱은 데모용 참고 도구이며, 의학적 진단을 대체하지 않습니다.
강아지 건강이 걱정되시면 반드시 동물병원과 상담해주세요.
