# 01_plan: Cortex AI Functions 구현 (Issue #27)

> Branch `feat/000027-cortex-ai-functions` · 작성 2026-04-08 (team `plan-27-cortex`: spec-aligner + impl-architect + compat-critic)
> SoT: `docs/specs/dev_spec.md` B4 (line 1599~1770, 2026-04-08 #40 재작성본)
> 병렬 리서치 산출물:
> - `.omc/research/27-plan-spec-alignment.md` (정정안 15건 + Red 테스트 6 TC)
> - `.omc/research/27-plan-impl-architecture.md` (937줄 — 3개 SQL + cortex.py 전체 본문)
> - `.omc/research/27-plan-compatibility.md` (의존성 그래프 + 리스크 10건 + Snowflake 사전 검증 7건)

---

## 0. 상황 요약 — 왜 01_plan.md를 재작성하는가

Issue #27 body(`00_issue.md`) + 기존 01_plan.md는 **#40 dev_spec 재작성 이전에 작성되어 stale**이다. 아래 5건은 즉시 교체 대상:

| # | stale 표기 | #40 이후 SoT |
|---|-----------|-------------|
| 1 | `mistral-large2` | `claude-4-sonnet` |
| 2 | `e5-base-v2` | `snowflake-arctic-embed-l-v2.0` (`VECTOR(FLOAT, 1024)`) |
| 3 | `SNOWFLAKE.CORTEX.COMPLETE/CLASSIFY/EMBED` (네임스페이스) | `AI_COMPLETE / AI_CLASSIFY / AI_AGG / AI_EMBED` (GA, 접두사 없음) |
| 4 | `'서울특별시'` (일부 예시) | `INSTALL_STATE = '서울'` (#40 Snowflake 직검증 정정) |
| 5 | `sql/tests/test_12_cortex_ai.sql` (복수형) | `sql/test/test_12_cortex_ai.sql` (본 레포 실경로) |

**전략:** 본 01_plan.md를 SoT 기준으로 전면 재작성하고, finish 단계에서 `00_issue.md` + `gh issue edit 27 --body-file` 로 1회 동기화한다.

---

## 1. AC 체크리스트 (재작성)

Issue #27 AC는 유지하되, 모델명·함수명·경로를 SoT 기준으로 교체한다. AI_AGG를 선택 AC로 추가(B4 MVP 4함수 커버리지 확보).

- [ ] **AC-01 · AI_COMPLETE 인사이트 생성 SQL 작동** — `AI_COMPLETE('claude-4-sonnet', <prompt>)` 호출로 비어있지 않은 한국어 문자열 반환. 실데이터(`V_TELECOM_NEW_INSTALL` + `MART_MOVE_ANALYSIS`) 기반 1행 이상 Green.
- [ ] **AC-02 · AI_CLASSIFY 이사 등급 분류 SQL 작동** — `AI_CLASSIFY(input, ARRAY_CONSTRUCT('긴급 — …','주의 — …','안정 — …'))` 가 3개 라벨 중 하나를 반환. Python 리스트 `[]` 문법 금지.
- [ ] **AC-03 · AI_EMBED + 벡터 유사도 검색 SQL 작동** — `AI_EMBED('snowflake-arctic-embed-l-v2.0', <text>)` 가 `VECTOR(FLOAT, 1024)` 반환, `VECTOR_COSINE_SIMILARITY` 로 유사 구 top-5 조회 가능.
- [ ] **AC-04 · Streamlit 연동 함수 구현** — `src/app/cortex.py` 4개 공개 함수(`get_district_insight` / `classify_demand` / `find_similar_districts` / `aggregate_state_summary`) 구현 + Dual-Tier 배지 반환.
- [ ] **AC-05 (권고) · AI_AGG 시군구 트렌드 요약 SQL 작동** — B4 MVP 4함수 커버리지. Red 테스트 TC-06로 검증.

---

## 2. 테스트 체크리스트 (TDD · `sql/test/test_12_cortex_ai.sql` · Red → Green)

Red SQL 전문은 `.omc/research/27-plan-spec-alignment.md` §3에 준비됨. 파일에 그대로 붙여넣어 실행.

- [ ] **TC-01** · `AI_COMPLETE('claude-4-sonnet', '한국어로 "안녕하세요"…')` → `LENGTH(result) > 0` — **모델 활성화 검증(R6)** 겸용
- [ ] **TC-02** · `AI_CLASSIFY('신규개통 150건, +25%', ARRAY_CONSTRUCT(…3개…))` → 결과 ∈ {긴급,주의,안정}
- [ ] **TC-03** · `AI_EMBED('snowflake-arctic-embed-l-v2.0', …)` → `TYPEOF LIKE 'VECTOR(FLOAT%1024%'` + NOT NULL
- [ ] **TC-04** · `V_TELECOM_NEW_INSTALL WHERE INSTALL_STATE='서울' LIMIT 1` 행을 프롬프트에 CONCAT → `AI_COMPLETE` 결과 LENGTH > 0
- [ ] **TC-05** · `VECTOR_COSINE_SIMILARITY(강남-서초, 강남-해운대)` → 두 값 FLOAT NOT NULL + 강남-서초 ≥ 강남-해운대
- [ ] **TC-06** · `AI_AGG(MART_MOVE_ANALYSIS 최신월 25구 concat, …)` → 1행 + summary LENGTH > 0

Python 통합 테스트는 선택 (`tests/test_12_cortex_ai.py`). CI 스모크는 SQL 6 TC로 충분.

---

## 3. 파일 구조 (산출물)

```
sql/cortex/                               ← 신규 디렉토리 (dev_spec A8 매핑)
├── .ai.md                                (신규) 목적·뷰/테이블/SP 목록·Dual-Tier 분기
├── 001_cortex_ai_insights.sql            (신규) V_AI_DISTRICT_INSIGHTS + V_AI_STATE_SUMMARY
├── 002_cortex_ai_classify.sql            (신규) V_AI_DEMAND_GRADE
└── 003_cortex_ai_embed.sql               (신규) T_DISTRICT_EMBEDDINGS + SP_REFRESH + SP_FIND_SIMILAR

sql/test/
└── test_12_cortex_ai.sql                 (신규) Red → Green 6 TC

src/app/                                  ← 신규 디렉토리 (dev_spec A8 C1~C5 매핑)
├── .ai.md                                (신규) Streamlit 앱 구조 — 본 이슈는 cortex.py만
└── cortex.py                             (신규) Snowpark 헬퍼 4 함수 + allowlist + TypedDict

tests/ (선택)
└── test_12_cortex_ai.py                  (선택) cortex.py 함수 실호출 스모크
```

**번호 규칙 결정:** `sql/cortex/`는 `sql/views/`(002~005)와 독립 네임스페이스로 **001부터** 시작. 근거 = dev_spec A8 L2906 디렉토리 분리 매핑. 테스트 번호 `test_12`는 이슈-테스트 1:1(#27→12) 규칙 유지.

---

## 4. 데이터베이스 객체 (완성 후 MOVING_INTEL.ANALYTICS 내 추가 객체)

| 종류 | 이름 | 의존성 | 역할 |
|------|------|--------|------|
| VIEW | `V_AI_DISTRICT_INSIGHTS` | MART_MOVE_ANALYSIS · V_RICHGO_MARKET_PRICE · V_BJD_DISTRICT_MAP | 25구 × 월 AI_COMPLETE 인사이트. `CASE DATA_TIER` 분기 프롬프트. |
| VIEW | `V_AI_STATE_SUMMARY` | MART_MOVE_ANALYSIS | 서울 월별 AI_AGG 자연어 요약. |
| VIEW | `V_AI_DEMAND_GRADE` | MART_MOVE_ANALYSIS | 25구 × 월 AI_CLASSIFY 3등급 (allowlist: 긴급/주의/안정). |
| TABLE | `T_DISTRICT_EMBEDDINGS` | MART_MOVE_ANALYSIS · V_RICHGO_MARKET_PRICE · V_BJD_DISTRICT_MAP | 25행 × `VECTOR(FLOAT, 1024)` 지역 프로필. ~100KB. |
| PROCEDURE | `SP_REFRESH_DISTRICT_EMBEDDINGS()` | T_DISTRICT_EMBEDDINGS | MERGE 증분 — 최신월 기준 재계산. |
| PROCEDURE | `SP_FIND_SIMILAR_DISTRICTS(target_city_code, top_k)` | T_DISTRICT_EMBEDDINGS | RESULTSET 반환 — 유사 구 top_k. |

**MART_MOVE_ANALYSIS에는 ALTER 금지** — `T_DISTRICT_EMBEDDINGS` 별도 테이블로 분리(R1·R2 해소). #22 MOVE_SIGNAL_INDEX 컬럼 추가와 충돌 없음.

---

## 5. Dual-Tier 분기 매트릭스

| 항목 | MULTI_SOURCE 3구 (11140·11560·11650) | TELECOM_ONLY 22구 |
|------|--------------------------------------|-------------------|
| 데이터 소스 | OPEN_COUNT · ELECTRONICS_FURNITURE_SALES · TOTAL_RESIDENTIAL_POP · NEW_HOUSING_BALANCE_COUNT · RICHGO 평당가 (5종) | OPEN_COUNT · RICHGO 평당가 (2종) |
| AI_COMPLETE 프롬프트 | `[정밀 Tier] …4종 시그널 종합…B2B 3줄 번호 액션` | `[근사 Tier] …통신 단일 소스 경량…2줄, 첫 줄 "데이터 신뢰도: 근사"` |
| AI_EMBED 프로필 텍스트 | 4종 시그널 + 평당가 | OPEN_COUNT + 평당가 |
| UI 배지 | 🎯 정밀 Tier (4종 시그널) | ⚡ 근사 Tier (통신 단일) |
| 분기 위치 | SQL `CASE DATA_TIER WHEN 'MULTI_SOURCE' THEN … ELSE …` (뷰 본문) | 동일 |
| Python 역할 | 배지 부착만 — 프롬프트는 SQL에서 확정 | 동일 |

**원칙:** 프롬프트 수정은 SQL 파일 한 곳(`001_cortex_ai_insights.sql`, `003_cortex_ai_embed.sql`)에서만. Python은 결과 포맷팅·배지만 담당.

---

## 6. Streamlit 헬퍼 API (`src/app/cortex.py`)

| 함수 | 시그니처 | 반환 | 소비 이슈 |
|------|---------|------|-----------|
| `get_district_insight` | `(session, city_code, year_month) -> DistrictInsight` | TypedDict(`ai_insight`, `data_tier`, `tier_badge`, `open_count`, `yoy_pct`) | #28 Streamlit 히트맵 — 행정동 클릭 시 상세 패널 |
| `classify_demand` | `(session, city_code, year_month) -> DemandGrade` | TypedDict(`demand_grade` ∈ allowlist 3개) | #28 히트맵 색상/범례 보조 |
| `find_similar_districts` | `(session, city_code, top_k=5) -> list[SimilarDistrict]` | list[TypedDict(`similarity`, `city_name`, `data_tier`)] | #29 Streamlit 세그먼트 — "유사 지역 5개" 탭 |
| `aggregate_state_summary` | `(session, install_state='서울', year_month) -> str` | 한국어 요약 1문단 | #29 보조 카드 (선택) |

**보안·안정성 3중 방어:**
1. `SEOUL_CITY_CODES: frozenset` + `_validate_city_code()` — allowlist 25구만 허용
2. `_validate_year_month()` — 6자리 숫자 정규식
3. `session.sql(..., params=[...]).collect()` — bind 파라미터 (f-string SQL 금지)

---

## 7. 구현 순서 (TDD · 9단계)

### 7.1 준비·검증 (블로커 차단)

1. **[V0 사전검증 · Snowflake MCP]** — 구현 시작 전 아래 7개 쿼리를 1회 실행해 레이어별 가용성 확인.
   - V1 `SELECT CURRENT_REGION()` → Oregon 확인
   - V2 `DESCRIBE VIEW V_TELECOM_NEW_INSTALL` + `SELECT DISTINCT INSTALL_STATE` → `'서울'`
   - V3 `DESCRIBE TABLE MART_MOVE_ANALYSIS` + `SELECT DATA_TIER, COUNT(DISTINCT CITY_CODE)` → `MULTI_SOURCE=3 / TELECOM_ONLY=22`
   - V4 `SELECT AI_COMPLETE('claude-4-sonnet', 'ping')` → **R6 해소**
   - V5 `SELECT TYPEOF(AI_EMBED('snowflake-arctic-embed-l-v2.0', 'test'))` → `'VECTOR(FLOAT, 1024)'` **R6 해소**
   - V6 `JOIN V_RICHGO_MARKET_PRICE × V_BJD_DISTRICT_MAP` — 3구 매칭
   - V7 AI_COMPLETE 1행 샘플 실행 시간 측정 — **R3 비용 추정**
   - **실패 시 대응:** `.omc/research/27-plan-spec-alignment.md` §5.1 분기표 참조. 모델 미활성화 시 대체 모델(`claude-3-5-sonnet` 등) 승인 프로세스로 에스컬레이션.

2. **Issue body + 01_plan.md 정정** — 본 문서는 이미 반영됨. `00_issue.md` 불변식 섹션은 finish 단계에서 `gh issue edit 27 --body-file` 과 함께 rewrite.

### 7.2 Red 단계 (테스트 먼저)

3. **`sql/test/test_12_cortex_ai.sql` 작성** — `27-plan-spec-alignment.md` §3의 6 TC SQL 그대로 파일에 저장. 이 시점에는 뷰가 없으므로 TC-04·TC-06만 참조 실패 가능, TC-01~03·05는 모델 ping 레벨로 통과할 수 있음(Cortex GA 전제).

### 7.3 Green 단계 (구현)

4. **`sql/cortex/.ai.md` 작성** — 디렉토리 목적·파일 역할·의존성·Dual-Tier 원칙 기술. CLAUDE.md 불변식: 모든 디렉토리 `.ai.md` 포함.

5. **`sql/cortex/001_cortex_ai_insights.sql` 작성 + 실행** — `27-plan-impl-architecture.md` §2 본문 그대로. 뷰 2개(`V_AI_DISTRICT_INSIGHTS`, `V_AI_STATE_SUMMARY`) 생성. **TC-04, TC-06 Green 목표.**
   - **주의:** 뷰 SELECT 시점마다 AI_COMPLETE 호출 → 검증은 단일 행 필터(`WHERE CITY_CODE='11680' AND STANDARD_YEAR_MONTH='202604'`)로만 실행.

6. **`sql/cortex/002_cortex_ai_classify.sql` 작성 + 실행** — `V_AI_DEMAND_GRADE` 생성. AI_CLASSIFY GA 반환 스키마 실측: `OBJECT{label,score}` vs 직접 `STRING`. 실측 후 `:label::STRING` 캐스팅 유지 여부 결정. **TC-02 Green 목표.**

7. **`sql/cortex/003_cortex_ai_embed.sql` 작성 + 실행** — `T_DISTRICT_EMBEDDINGS` + `SP_REFRESH_DISTRICT_EMBEDDINGS` + `SP_FIND_SIMILAR_DISTRICTS` 생성. 마지막에 `CALL SP_REFRESH_DISTRICT_EMBEDDINGS()` 로 25행 초기 로드. **TC-03, TC-05 Green 목표.**

8. **`src/app/.ai.md` + `src/app/cortex.py` 작성** — `27-plan-impl-architecture.md` §5 본문 그대로. 4 함수 + TypedDict + allowlist + bind 파라미터. **AC-04 만족.**

9. **(선택) `tests/test_12_cortex_ai.py` 작성** — 4 함수 실호출 1건씩 스모크. 세션 픽스처는 기존 `tests/test_06_snowpark.py` 패턴 재사용.

### 7.4 마무리

10. **전체 통합 검증** — `sql/test/test_12_cortex_ai.sql` 6 TC 전부 Green 확인 + `sql/cortex/` 전 파일 Snowflake 재실행 멱등성 확인.

11. **`.ai.md` 최신화** — `sql/cortex/.ai.md`, `src/app/.ai.md`, 필요 시 `sql/views/.ai.md` 크로스 레퍼런스.

12. **`scripts/check_invariants.py` 통과** (있는 경우) — 시크릿 하드코딩 0건, PII 실데이터 커밋 0건.

13. **Issue body 동기화** — `finish-issue` 시점에 `gh issue edit 27 --body-file 00_issue.md` 로 stale 표기 제거 1회 반영. diff는 `.omc/research/27-plan-spec-alignment.md` §4.2 참조.

---

## 8. 의존성 그래프 (간략)

```
#19 V_TELECOM_NEW_INSTALL ──┐
#17 V_RICHGO_MARKET_PRICE ──┼─→ #21 MART_MOVE_ANALYSIS ─→ #27 Cortex AI Functions ─┬─→ #28 Streamlit 히트맵
#20 V_BJD_DISTRICT_MAP ─────┘                          (본 이슈)                    └─→ #29 Streamlit 세그먼트
#40 dev_spec 정정 ─────────────────────────────────────→ #27
                                                                    (병렬 독립) #22/#23/#24/#25/#26
```

**전체 그래프 + 10건 리스크 표:** `.omc/research/27-plan-compatibility.md` §1, §4 참조.

---

## 9. 호환성 결론 (compat-critic 요약)

**#27 즉시 착수 가능. 블로커 없음.**

- 10건 Input 의존성 모두 머지 완료(`2a60614`, `3cfafdb`) 또는 GA.
- R1(MART 컬럼 충돌): T2 impl-architect가 `T_DISTRICT_EMBEDDINGS` 별도 테이블로 분리 — **해소**.
- R2(Marketplace ALTER 금지): 본인 DB에 테이블 생성 — **해소**.
- R4(Issue body stale): 본 01_plan.md rewrite + finish 단계 `gh issue edit` — **해소 경로 확정**.
- R6(모델 활성화): 구현 첫 단계 V4·V5 쿼리로 검증 — **블로커 전환 가능, 조기 감지**.
- R3(AI_COMPLETE 비용): 뷰 전수 SELECT 금지, 파라미터 기반 단일 행 호출 + Streamlit `@st.cache_data` 후속 이슈로 연결.
- #28/#29 후속 이슈 body에 AI 호출 지점 명시 1건씩 필요 → finish 단계에서 spec-aligner 후속 sync 권고.

---

## 10. 불변식 (재작성)

- **리전:** US West (Oregon, us-west-2). Cross-region inference 불필요.
- **모델 3종 고정:** completion=`claude-4-sonnet`, embed=`snowflake-arctic-embed-l-v2.0`, 벡터 차원=`VECTOR(FLOAT, 1024)`.
- **함수 네임스페이스 고정:** `AI_COMPLETE` / `AI_CLASSIFY` / `AI_AGG` / `AI_EMBED` / `VECTOR_COSINE_SIMILARITY` (GA, 접두사 없음). `SNOWFLAKE.CORTEX.*` 사용 금지.
- **배열 문법:** `ARRAY_CONSTRUCT(...)` — Python 리스트 `[]` 금지.
- **실데이터 필터:** `V_TELECOM_NEW_INSTALL.INSTALL_STATE = '서울'` (NOT `'서울특별시'`). `MART_MOVE_ANALYSIS` 는 `DATA_TIER` 기반 분기 유지.
- **Marketplace 원본 쓰기 금지:** RICHGO 등 외부 공유 테이블 `ALTER` 금지. 벡터·파생 컬럼은 본인 DB(`MOVING_INTEL.ANALYTICS`)에 별도 테이블.
- **테스트 경로:** `sql/test/test_12_cortex_ai.sql` (단수형, `sql/tests/` 아님).
- **시크릿 하드코딩 금지:** `account`, `password`, `token` 소스코드 유입 금지. MCP/환경변수 사용.
- **PII 커밋 금지:** 개인정보·실데이터 샘플 금지. 기대값(row count, 컬럼 존재)만 테스트에 명시.

---

## 11. 검증 · 완료 조건

- [x] `sql/test/test_12_cortex_ai.sql` TC-01 ~ TC-06 전부 Green (Snowflake 직접 실행) — `.omc/research/scratch-27/run_tests.log` PASS 6/6 (2026-04-09)
- [x] `V_AI_DISTRICT_INSIGHTS`, `V_AI_STATE_SUMMARY`, `V_AI_DEMAND_GRADE`, `T_DISTRICT_EMBEDDINGS` 객체 실존 확인 — `deploy_cortex.log` `successfully created.`
- [x] `CALL SP_REFRESH_DISTRICT_EMBEDDINGS()` 성공 + `T_DISTRICT_EMBEDDINGS` 25행 — 초기 로드 반환 `"latest_ym=202604, rows=25"`
- [x] `CALL SP_FIND_SIMILAR_DISTRICTS('11650', 5)` 5행 반환 — 중구 0.89·영등포 0.86·서대문 0.75·…·타겟 제외 확인 (`smoke_cortex_helpers.log`)
- [x] `src/app/cortex.py` 4 함수 import 성공 + `_validate_city_code`/`_validate_year_month` 경계 테스트 — pure-Python validator 11건 PASS
- [x] `sql/cortex/.ai.md`, `src/app/.ai.md` 최신화 — 두 파일 모두 초기 작성본이 현 상태와 일치
- [ ] `scripts/check_invariants.py` 통과 (있는 경우) — finish-issue 시 확인
- [ ] `docs/work/active/000027-cortex-ai-functions/00_issue.md` + GitHub Issue #27 body 동기화 — finish-issue 시 `gh issue edit 27 --body-file`
- [ ] PR 본문에 AI_COMPLETE 1행당 실행 시간/비용 추정 기재 (R3 완화 증거) — finish-issue 시 작성 (TC-04 5.1s / V7 2.7s / TC-06 AI_AGG 2.7s 기록 사용)
- [ ] `docs/work/done/000027-cortex-ai-functions/` 로 이동 (finish-issue 시)

---

## 12. 관련 파일 인덱스

**입력 의존성 (읽기 전용):**
- `docs/specs/dev_spec.md` L1599~1770 (B4), L2906 (A8), L2946~2989 (#40 변경 이력)
- `pipelines/preprocessing.py` — MART_MOVE_ANALYSIS 생성 로직
- `sql/views/002_richgo_views.sql`, `sql/views/003_sph_views.sql`, `sql/views/004_bjd_mapping.sql`, `sql/views/005_telecom_district_mapped.sql`
- `sql/test/test_06_integrated_mart.sql` — MART 컬럼 실증

**신규 산출물:**
- `sql/cortex/.ai.md`
- `sql/cortex/001_cortex_ai_insights.sql`
- `sql/cortex/002_cortex_ai_classify.sql`
- `sql/cortex/003_cortex_ai_embed.sql`
- `sql/test/test_12_cortex_ai.sql`
- `src/app/.ai.md`
- `src/app/cortex.py`
- `tests/test_12_cortex_ai.py` (선택)

**리서치 산출물 (팀 `plan-27-cortex`):**
- `.omc/research/27-plan-spec-alignment.md` — 정정안 15건 + Red 테스트 6 TC + 사전 검증 5개
- `.omc/research/27-plan-impl-architecture.md` — 3 SQL + cortex.py 전체 본문 + 비용 추정
- `.omc/research/27-plan-compatibility.md` — 의존성 그래프 + 리스크 10건 + merge 순서

---

*플랜 완성일: 2026-04-08. 다음 단계 → 7.1 준비·검증(Snowflake MCP V0 7건)부터 착수.*
