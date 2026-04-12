# 04 — 제출 체크리스트

> 이슈 #62 산출물. Snowflake Hackathon 2026 템플릿 Slide 3 요건 기준.
> 작성: 2026-04-10

---

## 템플릿 Slide 3 요건 체크

> 아래 항목은 `[DOWNLOAD TEMPLATE] Snowflake Hackathon 2026 (External).pptx` Slide 3 기준.
> 템플릿 파일 위치: `C:\Users\watch\Downloads\`

| # | 요건 | 충족 여부 | 근거 |
|---|---|---|---|
| 1 | 팀명 기입 | ✅ | "무빙 인텔리전스" — Slide 1 (`02_slide_contents.md`) |
| 2 | 조직/소속 기입 | ✅ | "Snowflake AI & Data Hackathon 2026 Korea" |
| 3 | 날짜 기입 | ✅ | 2026-04-10 |
| 4 | Problem Statement (Slide 4) | ✅ | Theme + Hypothesis + 3불릿 (`02_slide_contents.md §Slide 4`) |
| 5 | Insight 3개 (Slide 5·6·7) | ✅ | 데이터 선행성 / B2B 세그먼트 / 기술 차별화 |
| 6 | 데이터 출처 명시 | ✅ | Snowflake Marketplace 4종 (`02_slide_contents.md §데이터 출처`) |
| 7 | Snowflake 기술 활용 증거 | ✅ | Dual-Tier + Cortex AI + Streamlit in Snowflake |
| 8 | 비즈니스 가치 / 확장 방향 | ✅ | Slide 7 확장 박스 + `03_speech_script.md §7` |

---

## 데모 스크린샷 첨부 가이드

PPT에 첨부할 스크린샷 3장을 캡처한다.

| 순서 | 화면 | 탭/기능 | 파일명 제안 |
|---|---|---|---|
| 1 | 서울 25구 이사 수요 히트맵 | 히트맵 탭 | `demo_01_heatmap.png` |
| 2 | 영등포 ROI 시뮬레이션 결과 | ROI 탭 → 영등포(11560) 선택 | `demo_02_roi_yeongdeungpo.png` |
| 3 | Cortex Analyst 자연어 질의 결과 | Cortex AI 탭 → "다음 달 서초구 이사 수요 예측해줘" | `demo_03_cortex_analyst.png` |

**캡처 방법**:
1. Snowflake 계정 로그인 → Streamlit 앱 실행
2. 각 탭 이동 후 Windows Snip & Sketch (Win+Shift+S) 또는 전체 화면 캡처
3. PPT Slide 7 발표자 노트 영역 또는 별도 슬라이드에 삽입

**백업 준비 (데모 실패 대비)**:
- 3장 스크린샷을 Slide 7 발표자 노트에 미리 첨부
- 데모 접속 실패 시 해당 스크린샷으로 대체 시연

---

## 불변식 위반 체크

| 항목 | 상태 |
|---|---|
| Snowflake 연결 정보 하드코딩 없음 | ✅ PPT에 계정 정보 미포함 |
| 실데이터 샘플 미포함 | ✅ 수치는 집계 통계만 (개인정보 없음) |
| 5MB 초과 파일 없음 | ✅ 마크다운 문서만 커밋 대상 |
| *.pdf, *.pptx 커밋 금지 | ✅ PPT 파일 자체는 .gitignore 대상 |

---

## 최종 제출 전 확인

- [ ] PPT 템플릿 Slide 1·4~7 콘텐츠 입력 완료
- [ ] 데모 스크린샷 3장 PPT에 첨부
- [ ] 10분 발표 대본 낭독 연습 1회 (±30초 이내)
- [ ] Slide 3 요건 8개 전부 충족 확인
- [ ] 제출 플랫폼 업로드 완료
