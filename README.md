🐕 일어나 파트라슈

노견(시니어 강아지) 보호자를 위한 건강 모니터링 미니 앱입니다.
강아지의 체중 변화, 건강 상태, 복약 여부, 일상 케어 기록을 한 화면에서 관리할 수 있도록 구성했습니다.

실행 방법
pip install -r requirements.txt
streamlit run app.py

로컬 환경에서 streamlit 명령어가 바로 실행되지 않는 경우 아래 명령어를 사용할 수 있습니다.

py -m streamlit run app.py
주요 기능
사이드바 프로필: 강아지 이름, 나이, 견종 입력 → 시니어 단계 자동 표시
⚖️ 체중관리: 체중 입력 → 기록 누적 → 체중 변화 추이 그래프 표시
🩺 건강체크: 시니어 건강 체크리스트 4문항 → 점수 합산 → 양호 / 관찰 필요 / 병원 상담 권장 판정
💊 복약알리미: 약 이름과 복용 시간 등록 → 오늘 복용 여부 체크 → 진행률 표시
📔 케어기록: 산책 시간과 한줄 메모를 기록하여 최근 케어 이력 확인
광고 배너: 사이드바 광고 이미지와 하단 배너 광고 표시
프로젝트 구성
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
사용 기술
Python
Streamlit
Pandas
Altair
Session State
충족 요소 체크
✅ 위젯 2개 이상 사용: text_input, slider, selectbox, number_input, button, radio, checkbox, text_area 등
✅ 레이아웃 사용: sidebar, tabs, columns
✅ session_state 활용: weight_log, health_history, medicines, med_check_today, care_log
✅ 시각화 요소: 체중 변화 추이 그래프
✅ 꾸미기 요소: 이모지, 색상 테마, 이미지 광고, toast 메시지, progress bar
주의사항

이 앱은 데모용 참고 도구이며, 의학적 진단을 대체하지 않습니다.
강아지의 건강 이상이 의심될 경우 반드시 동물병원과 상담해야 합니다.
