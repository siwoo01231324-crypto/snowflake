# 작업 플랜 — #62 해커톤 제출 PPT 콘텐츠 작성 및 제출 준비

> 작성: 2026-04-10 | Ralplan consensus (Planner→Architect→Critic 2-iter)

---

## AC 체크리스트

- [ ] **Slide 1 (Title)**: 팀명·조직·날짜 기입
- [ ] **Slide 4 (Problem Statement)**: Theme + Hypothesis 작성 — "통신 신규 계약은 이사 2~4주 선행, r=0.895" 포함
- [ ] **Slide 5 (Insight #1 — 데이터 선행성)**: CONTRACT→OPEN lag 증거 3불릿 (lag r=0.895 / KOSIS 후행 30~45일 / 부동산 계약~잔금 2~3개월)
- [ ] **Slide 6 (Insight #2 — B2B 비즈니스 기회)**: 3구 프로파일 기반 고객 세그먼트 3불릿 (중구 단신직장인 / 영등포 가전·가구 / 서초 학군지)
- [ ] **Slide 7 (Insight #3 — Snowflake 기술 차별화)**: Dual-Tier + Cortex AI + Streamlit in Snowflake 3불릿 + 확장방향
- [ ] **추후 확장 방향**: Dynamic Table + Task + Cortex Agents + 전국 확장
- [ ] **제출 체크리스트 확인**: 템플릿 Slide 3 요건 전부 충족 여부 점검
- [ ] **데모 링크 또는 스크린샷** 첨부 (Streamlit 대시보드 캡처)

---

## RALPLAN-DR

### Principles
1. **수치 정확성**: 모든 통계는 소스 문서 인용 (r, p, n 전부 명시)
2. **청중 중심 스토리텔링**: 심사위원(기술+비즈니스 양면)이 이해하는 순서로
3. **제약 투명성**: 데이터 한계는 슬라이드 텍스트에만, 발화 시간은 긍정 증거에 집중
4. **Snowflake Native 차별화**: 외부 서버 0, 단일 계정 내 ML→UDF→대시보드
5. **방어 준비**: 상관관계 공격, MAPE 미달성, 데모 실패 — 3대 리스크 사전 대응

### Decision Drivers
1. 10분 시간 제약 (과부하 방지)
2. 기술 트랙 심사위원 — 작동하는 데모 비중 높음
3. 통계 공격 방어 — carryover 28~30% 가 핵심 방어선

### Viable Options
| 옵션 | Pros | Cons |
|---|---|---|
| **A. 문제→증거→B2B→기술(현재 선택)** | 비즈니스 스토리 흐름 자연스러움 | 기술 데모가 후반부, 압박 구간 |
| B. 기술→데모→문제→B2B | 데모 임팩트 앞부분 | 문제 정의 없는 데모는 의미 약함 |

**선택 근거**: 심사위원이 "이 데이터가 왜 가치 있는가"를 이해하지 못한 상태에서 데모를 보면 임팩트가 희석됨. 옵션 A 유지, 단 데모 시간 확대.

---

## 구현 계획

### 산출물 4종

| # | 파일 | 내용 |
|---|---|---|
| 1 | `docs/presentation/02_slide_contents.md` | Slide 1·4~7 확정 텍스트 (헤드라인 + 불릿 + 발표자 노트) |
| 2 | `docs/presentation/03_speech_script.md` | 10분 발표 대본 (7구간, 구어체, 타이밍, 전환 멘트) |
| 3 | `docs/presentation/04_submission_checklist.md` | 템플릿 Slide 3 요건 체크 + 데모 스크린샷 안내 |
| 4 | `.ai.md` 최신화 | docs/presentation/.ai.md에 02~04 추가 |

### 타이밍 배분 (Architect 권고 반영, 데모 +45s)

| 구간 | 시간 | 초 | 슬라이드 | 핵심 행동 |
|---|---|---|---|---|
| 오프닝 훅 | 0:00~0:45 | 45s | Slide 1 | 시장 규모 1문장 + 문제 선언 |
| Problem Statement | 0:45~2:15 | 90s | Slide 4 | 골든 윈도우 부재 → 가설 |
| Insight #1 증거 | 2:15~4:00 | 105s | Slide 5 | Layer 1·2만 발화 (Layer 3·4 슬라이드에만) |
| Insight #2 B2B | 4:00~5:30 | 90s | Slide 6 | 3구 세그먼트 1불릿씩 |
| Insight #3 기술+데모 | 5:30~8:15 | 165s | Slide 7 | 아키텍처 30s + 데모 2:15 |
| 확장 로드맵 | 8:15~9:30 | 75s | Slide 7 하단 | Phase 0→3 1문장씩 |
| 클로징 | 9:30~10:00 | 30s | Slide 1 재귀 | 핵심 명제 재각인 |

**총계**: 600초 (±15s per section 허용)

### 작업 순서

**Step 1**: `02_slide_contents.md` 작성
- Slide 1: 팀명(무빙 인텔리전스), 조직(Snowflake Korea Hackathon 2026), 날짜(2026-04-10)
- Slide 4: Theme "Signal Gap in Moving Market" + Hypothesis 3불릿
- Slide 5: Insight #1 제목 + 3불릿 (r=0.895 / KOSIS r≈0.002 역설 / 법률+부동산 upper bound)
- Slide 6: Insight #2 제목 + 3불릿 (중구/영등포/서초 1불릿씩)
- Slide 7: Insight #3 제목 + 3불릿 + 확장 4개 아이템

**Step 2**: `03_speech_script.md` 작성
- 한국어 구어체, 자연스럽게
- 각 구간 타임스탬프 + 발화 스크립트 + 전환 멘트
- **필수 포함**: Slide 5에서 carryover 방어 멘트 — "상관계수가 처리 지연 아닌가 물으실 수 있습니다. 맞습니다. 그 28~30%가 바로 골든 윈도우입니다."
- **MAPE 표현**: "목표"로 통일 (달성 여부 미확인 시), 실측값 있으면 교체
- 슬라이드-대본 교차참조 테이블 포함

**Step 3**: `04_submission_checklist.md` 작성
- 템플릿 Slide 3 요건 항목별 충족 여부
- 데모 스크린샷: 어떤 화면을 캡처할지 명시 (히트맵 / ROI / Cortex Analyst 결과)
- 데모 백업: 정적 스크린샷 준비 경로

**Step 4**: AC 점검 + `.ai.md` 최신화

---

## 리스크 완화

| 리스크 | 발생 가능성 | 완화 방안 |
|---|---|---|
| r=0.895 상관관계 공격 ("처리 지연 아닌가?") | 높음 | 대본 Step 2에 carryover 28~30% 방어 선제 삽입 |
| MAPE 달성 미확인 | 중간 | "목표" 표현 사용, 실측값 있으면 교체 |
| 데모 실패 (타임아웃, 네트워크) | 중간 | 백업 스크린샷 3장 준비 (히트맵·ROI·Cortex) |
| 10분 초과 | 중간 | 각 구간 ±15s 허용, 확장 로드맵 75s에서 여유분 확보 |

---

## 검증 기준

- [ ] 각 슬라이드 불릿의 수치가 `00_pitch_story.md` / `01_district_profiles.md` 와 일치
- [ ] 대본 전체 낭독 시 10분 ±30s 이내
- [ ] Slide 5 carryover 방어 멘트 포함 여부
- [ ] MAPE 표현이 "목표" 또는 실측값으로 통일
- [ ] 슬라이드-대본 교차참조 테이블 존재

---

## 참고 문서

- `docs/presentation/00_pitch_story.md` — 4중 증거 체인, Q&A 8건, 기존 5분 대본
- `docs/presentation/01_district_profiles.md` — 3구 카드 수치
- `docs/whitepaper/v1.0-moving-intelligence.md` — B2B 세그먼트·수익 모델
- `docs/specs/dev_spec.md` §B4~B5 — Cortex AI 구현 상세
