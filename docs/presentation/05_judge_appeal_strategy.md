# 05 — 심사위원 어필 전략 (Hackathon Strength Mapping)

> 이슈 #62 산출물. `docs/background/snowflake-meetup-summaries.md` 의 2026 해커톤 가이드 세션
> (이재면·성순모·박준호·전수범·성지욱·심동현) 교훈을 우리 프로젝트 강점으로 매핑한다.
> 작성: 2026-04-11

---

## 0. 핵심 메시지

> **"가장 강력한 모델이 아니라, Snowflake 기능을 가장 잘 활용한 팀이 이긴다."**
> — 성순모 (Data SuperHero), 성지욱 (해커톤 Top 3)

우리는 Marketplace, Snowpark ML, UDF, Cortex AI 4종, Streamlit in Snowflake —
**6개 Snowflake 기능 레이어를 단일 계정 내에서 완결**했다.

---

## 1. 심사 기준 대응 (이재면 SuperHero 가이드)

이재면님이 공개한 Tech Track 심사 기준 5개 × 우리 프로젝트 증거:

| 심사 기준 | 우리 대응 | 근거 |
|---|---|---|
| **창의성** | 통신 신규 계약이 이사보다 1개월 선행한다는 **구조적 발견** — 공공 통계(KOSIS 전입신고)로는 구조적으로 포착 불가능한 선행성을 r=0.895(p<0.001, n=841)로 실증 | `00_pitch_story.md §4.1~4.2` |
| **Snowflake 기능 활용도** | Marketplace(4종) + Snowpark Python + Snowpark ML + SQL UDF + Cortex AI(4종) + Streamlit in Snowflake = **6개 레이어 단일 계정 완결**, 외부 서버 0 | `02_slide_contents.md §Slide 4 기술스택` |
| **AI 기능 활용** | AI_COMPLETE(B2B 인사이트) + AI_CLASSIFY(수요 등급) + Cortex Analyst(자연어 질의) + AI_EMBED(유사 구 검색) — **Cortex AI 4종 동시 활용** | `sql/cortex/*.sql`, `src/app/tabs/cortex_ai.py` |
| **현실성·실현가능성** | 연 628만 이사 × 200~500만원 = **1.5조원+ B2B 시장**, 실제 타겟 고객(통신사·렌탈사·인테리어·금융) 명시, Year 1 ARR 13억 목표, Dual-Tier 프레임워크로 **Marketplace 구독만 늘려도 전국 즉시 확장** | `docs/whitepaper/v1.0-moving-intelligence.md §5` |
| **스토리텔링** | 페인포인트(시그널 공백) → 가설(통신 선행) → 검증(r=0.895) → B2B 가치(3구 맞춤 세그먼트) → 기술(Dual-Tier) → 확장(전국) — **하나의 단단한 내러티브** | `03_speech_script.md` 전체 |

---

## 2. "남들이 안 보는 지표" 매칭 (박준호 교훈)

박준호님(CDO, 2025 해커톤 Top 3)의 핵심 교훈:
> "남들이 안 보는 지표를 찾아라. 백화점 방문자 수를 주식 지표로 썼다."

| 박준호(2025) | 무빙 인텔리전스(2026) |
|---|---|
| 백화점 방문자 수 → 주가 선행 지표 | **통신 신규 계약 → 이사 선행 지표** |
| 위치기반 데이터(로플렛) | Snowflake Marketplace 아정당 통신 데이터 |
| 백테스팅 + 손익 시뮬레이션 | Walk-forward 검증 + 4중 증거 체인 |
| Claude LLM 투자 인사이트 챗봇 | **Cortex AI 4종** + Cortex Analyst 자연어 질의 |

**공통 패턴**: 원래 다른 용도(통신 계약/방문자)인 데이터를 **선행 지표로 재해석** + Snowflake Marketplace 원클릭 연동 + AI 인사이트 레이어.

---

## 3. Cortex Code(코코) 10스킬 커버리지 (성순모 가이드)

성순모님이 제시한 "해커톤 우승을 결정하는" Cortex Code 10스킬 × 우리 활용:

| Cortex 스킬 | 우리 활용 여부 | 적용 파일 |
|---|---|---|
| **AI Functions** (★★★) | ✅ AI_COMPLETE, AI_CLASSIFY, AI_EMBED 모두 활용 | `sql/cortex/001_cortex_ai_insights.sql`, `sql/cortex/002_cortex_ai_classify.sql` |
| **Machine Learning** (★★★) | ✅ Snowpark ML + Registry + Track A/B 학습 | `ml/run_training.py`, `ml/train.py` |
| **Notebook Workspace** (★★★) | ✅ 학습·검증 노트북 | `notebooks/` (예정) |
| **Integrations** (★★★) | ✅ Marketplace 4종 참조 뷰 직결 | `sql/views/*.sql` |
| **Data Governance** (★★) | ✅ RBAC + 법정동 단위 집계만 (PII 없음) | `docs/specs/dev_spec.md A1` |
| **Data Quality** (★★) | ✅ DATA_TIER 검증 + walk-forward split | `ml/train.py:133` |
| **Lineage** (★★) | ✅ Marketplace → MART → UDF → Streamlit 단방향 | 아키텍처 다이어그램 |
| **Cost Intelligence** (★★) | ⚪ 해커톤 범위 밖 (확장 방향) | — |
| **Data Clean Room** (★) | ⚪ 해커톤 범위 밖 | — |
| **dbt Project** (★★) | ⚪ Snowpark Python 직접 사용 | — |

**커버리지**: 7/10 스킬 활용 (★★★ 4개 전부 활용).

---

## 4. Semantic Layer 구조 (전수범 풀무원 사례)

전수범님의 핵심 메시지:
> "AI 에이전트 이전에 Semantic Layer가 먼저다. 좋은 데이터 구조가 AI 활용의 선결 조건."

### 우리의 Medallion + Semantic Layer 매핑

```
Bronze (Marketplace 원본)
  ├── V_TELECOM_NEW_INSTALL (아정당 통신)
  ├── V_SPH_FLOATING_POP / CARD_SALES / ASSET_INCOME (SPH)
  ├── V_RICHGO_MARKET_PRICE (RICHGO)
  └── V_BJD_DISTRICT_MAP (법정동 마스터)

Silver (정제·표준화)
  ├── V_TELECOM_DISTRICT_MAPPED (BJD → CITY_CODE 매핑)
  ├── V_DISTRICT_PROFILE_3GU (3구 카드 집계)
  └── TMP_KOSIS_MOVE_REF (KOSIS 교차검증용)

Gold (의사결정용 KPI)
  └── MART_MOVE_ANALYSIS (850행, DATA_TIER 분기 컬럼)

Semantic Layer (AI 에이전트 소비용)
  ├── PREDICT_MOVE_DEMAND(city_code, ym) — 단일 진입점 UDF
  ├── CALC_ROI(city_code, industry, budget) — ROI 시뮬레이션 UDF
  ├── V_AI_DISTRICT_INSIGHTS — AI_COMPLETE 인사이트 뷰
  ├── V_AI_DEMAND_GRADE — AI_CLASSIFY 수요 등급 뷰
  └── Cortex Analyst Semantic Model (YAML)
```

**강조 포인트**: 전수범님이 "AI 에이전트가 바로 소비할 수 있는 Semantic Layer"를 Snowflake 아키텍처의 핵심이라고 말했는데, 우리 `MART_MOVE_ANALYSIS` + 4개 UDF + 2개 AI 뷰가 정확히 그 역할을 한다.

---

## 5. 성지욱 후회 방지 (Snowflake 고급 기능 100% 활용)

성지욱님(2025 Top 3, NextGen Index)의 자기 성찰:
> "Snowflake 고급 기능(생성 AI, 자동 보고서 등) 미활용이 아쉬웠다. 제공 기능을 100% 활용하는 전략이 유리하다."

### 우리가 활용한 고급 기능 체크리스트

- [x] **Snowflake Marketplace** — 4종 구독, 참조 뷰 직결
- [x] **Snowpark Python** — `pipelines/preprocessing.py` MART 구축
- [x] **Snowpark ML + Model Registry** — `ml/run_training.py` Track A/B 학습·배포
- [x] **Snowflake SQL UDF** — `PREDICT_MOVE_DEMAND`, `CALC_ROI`
- [x] **Cortex AI — AI_COMPLETE** — B2B 업종별 전략 자동 생성
- [x] **Cortex AI — AI_CLASSIFY** — 수요 등급 분류 (긴급/주의/안정)
- [x] **Cortex AI — AI_EMBED** — 유사 구 벡터 검색
- [x] **Cortex Analyst** — 자연어 SQL 질의
- [x] **Streamlit in Snowflake** — 3탭 네이티브 대시보드
- [ ] **Dynamic Table** — 확장 방향 (향후)
- [ ] **Snowflake Task** — 확장 방향 (향후)
- [ ] **Cortex Agents** — 확장 방향 (향후)

**달성**: 9개 핵심 기능 + 3개 확장 로드맵 명시.

---

## 6. 발표 프레이밍 강화 (이재면 치트키 적용)

이재면 SuperHero가 강조한 발표 원칙:

### ❌ 금지 — "기능 나열"
```
"저희는 Snowpark ML을 사용해서 XGBoost 모델을 학습했고,
UDF로 배포했고, Streamlit으로 시각화했고..."
```

### ✅ 권장 — "문제→해결"
```
"이사 1건당 200만원이 소비되는데, 아무도 이사를 모릅니다.
저희는 통신 신규 계약이 이사보다 1개월 먼저 발생한다는 걸 발견했습니다.
r=0.895로 검증했고, 이걸 B2B에 팔 수 있는 구조로 만들었습니다."
```

### 적용 완료 위치
- `03_speech_script.md §1 오프닝` — 문제 → 가설 → 우리 해결책
- `03_speech_script.md D-4 솔루션` — 페인포인트 다시 요약 후 해결 증거
- `02_slide_contents.md §Slide 4` — 문제 정의 섹션을 최상단에 배치

### 추가 적용 필요
- [ ] 데모 영상 오프닝 30초에 "1.5조원 시장, 아무도 이사를 모른다" 문제 선언
- [ ] 창의성 증명 = 특허 신규성·진보성 논리 → "공공 통계로는 구조적으로 포착 불가능" 프레이즈 반복 3회 이상

---

## 7. 일정 리스크 (4/29 파이널 필참)

> "불참 즉시 수상 자격 박탈" — 이재면

| 일정 | 날짜 | 상태 |
|---|---|---|
| 과제 제출 마감 | **2026-04-12** | D-1 (내일) |
| 최종 결선 진출자 발표 | 2026-04-20 | 대기 |
| **파이널 결선 (강남, 오프라인)** | **2026-04-29** | **필참** — 일정 확보 |

### 오늘(04-11)~내일(04-12) 할 일
- [ ] PPT 템플릿 Slide 1·4~7 실제 입력 (`02_slide_contents.md` 기준)
- [ ] 데모 녹화 영상 촬영 (`03_speech_script.md` 기준, 6개 슬라이드)
- [ ] 템플릿 + 영상 + 데모 스크린샷 해커톤 홈페이지 제출
- [ ] 4/29 파이널 일정 캘린더 등록

---

## 8. 발표 체크리스트 (최종 점검)

심사 기준 × 실전 체크:

- [ ] **창의성**: "구조적으로 포착 불가능한 선행성" 프레이즈 슬라이드·대본 3회 이상
- [ ] **Snowflake 활용**: 6개 레이어(Marketplace/Snowpark/ML/UDF/Cortex/Streamlit) 다이어그램 명시
- [ ] **AI 활용**: Cortex 4종(Complete/Classify/Analyst/Embed) 시연 또는 화면 포함
- [ ] **현실성**: 1.5조원 시장 + 실제 B2B 고객명(통신사·렌탈·인테리어·금융) 명시
- [ ] **스토리텔링**: 문제 → 가설 → 검증 → 가치 → 기술 → 확장 순서 견지
- [ ] **간결함**: 스펙 나열 없이, 문제·임팩트 중심

---

## 출처

- `docs/background/snowflake-meetup-summaries.md` §1~7 (성지욱·박준호·심동현·이재면·전수범·성순모·일정)
- `docs/presentation/00_pitch_story.md` (4중 증거 체인·B2B 가치)
- `docs/presentation/01_district_profiles.md` (3구 프로파일)
- `docs/presentation/02_slide_contents.md` (과제 템플릿 콘텐츠)
- `docs/presentation/03_speech_script.md` (데모 영상 대본)
