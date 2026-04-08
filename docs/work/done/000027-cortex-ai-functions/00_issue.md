# feat: Cortex AI Functions 구현 (AI_COMPLETE/AI_CLASSIFY/AI_EMBED)

## 목적
AI가 이사 등급 분류, 인사이트 요약, 벡터 검색을 해주는 Cortex AI Functions SQL을 구현한다.

## 완료 기준
- [x] AI_COMPLETE 인사이트 생성 SQL 작동 — `V_AI_DISTRICT_INSIGHTS` + `V_AI_STATE_SUMMARY` Snowflake 배포, 서초구 2024-12 정밀 Tier 3줄 액션 / 강남구 2026-04 근사 Tier 2줄 + 신뢰도 고지 모두 runtime 확인 (2026-04-09)
- [x] AI_CLASSIFY 이사 등급 분류 SQL 작동 (ARRAY_CONSTRUCT 문법) — `V_AI_DEMAND_GRADE` 배포, 서초구 2024-12 → `'안정'` 반환, `:labels[0]::STRING` 추출 경로 검증
- [x] AI_EMBED + 벡터 유사도 검색 SQL 작동 — `T_DISTRICT_EMBEDDINGS` 25행 + `SP_FIND_SIMILAR_DISTRICTS('11650',5)` → 중구 0.89 · 영등포 0.86 · 서대문 0.75 (벡터 의미 정합성 확인: MULTI_SOURCE 3구 상호 상위)
- [x] Streamlit 연동 함수 구현 — `src/app/cortex.py` 4 공개 함수 + TypedDict + allowlist + bind 파라미터, pure-Python validator 11건 + runtime smoke 6건 PASS

## 테스트 코드 (TDD — 먼저 작성)

```sql
-- test_12_cortex_ai.sql
-- TC-01: AI_COMPLETE 호출 가능
SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '서울 강남구 이사 수요 분석해줘') AS insight;
-- EXPECTED: 비어있지 않은 문자열 반환

-- TC-02: AI_CLASSIFY 등급 분류 (ARRAY_CONSTRUCT 문법)
SELECT SNOWFLAKE.CORTEX.CLASSIFY(
    '신규개통 150건, 전월 대비 +25%',
    ARRAY_CONSTRUCT('긴급 — 즉시 마케팅 투입', '주의 — 모니터링 필요', '안정 — 일반 운영')
) AS grade;
-- EXPECTED: 3개 등급 중 하나 반환

-- TC-03: AI_EMBED 벡터 생성
SELECT SNOWFLAKE.CORTEX.EMBED('e5-base-v2', '강남구 아파트 시세') AS vec;
-- EXPECTED: VECTOR 타입 반환, 차원 > 0

-- TC-04: 실제 테이블 데이터로 AI_COMPLETE 호출
SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2',
    CONCAT('지역: ', v.INSTALL_CITY, ', 신규개통: ', v.OPEN_COUNT, '건. 분석해줘.')
) AS insight
FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL v
LIMIT 1;
-- EXPECTED: 의미있는 분석 텍스트 반환
```

## 참조
- `docs/specs/dev_spec.md` B4 (Cortex AI Functions)
- AI_CLASSIFY 배열은 반드시 ARRAY_CONSTRUCT() 사용 (Python 리스트 `[]` 문법 아님)
- 의존성: #21 (통합 마트)

## 불변식
- Cortex AI Functions는 US West Oregon 리전에서 전체 지원
- AI_COMPLETE 모델: mistral-large2 (비용 효율)
- AI_EMBED 모델: e5-base-v2

## 작업 내역

### 2026-04-08 — /ri 현황 점검
- 브랜치: `feat/000027-cortex-ai-functions` (이슈 #27)
- AC 진행: 0/4 (모두 미완료)
- 단계: **구현 대기** — 미커밋 변경사항 없음, 작업 폴더(`00_issue.md`, `01_plan.md`)만 존재
- 의존성 #21 통합 마트는 머지 완료(`2a60614`) — 본 이슈 착수 가능
- 다음 액션: `sql/tests/test_12_cortex_ai.sql` 작성(Red) → AI_COMPLETE/CLASSIFY/EMBED 래퍼 → Streamlit 연동

### 2026-04-09 — Green 완료 스냅샷 (Python connector 직접 실행)
- Snowflake MCP 끊김 → `snowflake-connector-python` 으로 우회 (`~/.snowflake/connections.toml [default]`)
- 스크래치 스크립트 (`.omc/research/scratch-27/`, gitignored):
  - `v0_sanity.py`/`v0_sanity2.py`/`v0_sanity3.py` — 전제 조건 검증 (Oregon, MART DATA_TIER 3:22, AI_COMPLETE/AI_EMBED 활성화, RICHGO 커버리지)
  - `deploy_cortex.py` — `sql/cortex/001~003.sql` 순차 실행
  - `run_tests.py` — `sql/test/test_12_cortex_ai.sql` TC-01~TC-06 수동 split 실행 + PASS/FAIL 판정
  - `smoke_cortex_helpers.py` — `src/app/cortex.py` 순수 검증자 테스트 + 뷰/SP runtime 호출
- **배포 결과 (Snowflake 실제 생성):**
  - `V_AI_DISTRICT_INSIGHTS`, `V_AI_STATE_SUMMARY` ✓
  - `V_AI_DEMAND_GRADE` ✓
  - `T_DISTRICT_EMBEDDINGS` (VECTOR(FLOAT, 1024) × 25행) ✓
  - `SP_REFRESH_DISTRICT_EMBEDDINGS` / `SP_FIND_SIMILAR_DISTRICTS` ✓
  - 초기 로드: `T_DISTRICT_EMBEDDINGS refreshed (latest_ym=202604, rows=25)`
- **TC-01~TC-06 결과 (`.omc/research/scratch-27/run_tests.log`):** PASS 6 / FAIL 0
  - TC-01 AI_COMPLETE "안녕하세요" · 2.9s
  - TC-02 AI_CLASSIFY `'안정'` · 0.6s
  - TC-03 AI_EMBED NOT NULL · 0.6s
  - TC-04 송파구 1151건 → 3줄 B2B 액션 아이템 · 5.1s
  - TC-05 강남-서초 0.837, 강남-해운대 0.504 (벡터 의미 정합) · 1.9s
  - TC-06 "송파구 1145건 최고, 종로구 258건 최저" · 2.7s
- **AC-04 runtime smoke (`smoke_cortex_helpers.log`):** PASS 17 / FAIL 0
  - Pure Python validators 11건 (allowlist 25구 · city_code/year_month 경계 조건)
  - Runtime 6건 (서초 MULTI_SOURCE 3줄 액션 · 강남 TELECOM_ONLY 신뢰도 고지 · AI_CLASSIFY 서초 '안정' · SP_FIND_SIMILAR 서초 top-5: 중구 0.89 영등포 0.86 서대문 0.75 · AI_AGG 202412 25구 요약 · T_DISTRICT_EMBEDDINGS 25행)
- **데이터 한계 관찰 (신규 발견):**
  - `V_RICHGO_MARKET_PRICE` 및 SPH 소스 월 범위 최대 = `202412`
  - `MART_MOVE_ANALYSIS` 월 범위 = `202307~202604` (34개월)
  - → MULTI_SOURCE 3구의 4종 시그널(평당가·상주인구·카드매출·신규주거잔고)은 2024-12까지만 완전
  - 현재 `SP_REFRESH_DISTRICT_EMBEDDINGS`는 `MAX(STANDARD_YEAR_MONTH)=202604` 기준 → 3구 프로필 텍스트에 "0원/N/A" 포함 → 임베딩 품질 약화 가능성
  - 벡터 유사도 검증 결과 정성적으로는 여전히 정합(중구·영등포·서초가 상위 군집) → **후속 개선 후보** (#28/#29 이슈 또는 별도 hotfix)
- **본 이슈 안에서 추가로 처리한 개선 (SP Tier-aware 기준월 분기):**
  1. `sql/cortex/003_cortex_ai_embed.sql` — `SP_REFRESH_DISTRICT_EMBEDDINGS` 재작성: `multi_ym = MAX(YM WHERE DATA_TIER='MULTI_SOURCE' AND AVG_MEME_PRICE IS NOT NULL)` / `telecom_ym = MAX(YM WHERE DATA_TIER='TELECOM_ONLY')`
  2. `T_DISTRICT_EMBEDDINGS` — `PROFILE_YM VARCHAR(6)` 컬럼 추가 (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS` 로 idempotent), 관측성 확보
  3. `sql/cortex/.ai.md` — "임베딩 Tier별 기준월" 섹션 추가
  4. 재배포 결과: `T_DISTRICT_EMBEDDINGS refreshed (multi_ym=202412, telecom_ym=202604, rows=25)` — MULTI_SOURCE 3구 → 202412, TELECOM_ONLY 22구 → 202604 실측 확인
  5. **품질 개선 효과 (`verify_tier_aware.log`):**
     - 이전: 서초구 프로필 "신규개통 X건, 상주인구 0명, 가전매출 0원, 평당 N/A원"
     - 지금: 서초구 프로필 "신규개통 462건, 상주인구 3962711명, 가전매출 9454712863원, 신규주거잔고 1620건, 평당 7181원"
     - 서초구 유사 top-5: 이전 `중구 0.89 · 영등포 0.86 · 서대문 0.75` → 지금 `중구 0.908 · 영등포 0.859 · 서대문 0.653 · 중랑 0.636 · 성동 0.622`
     - **Tier 간 분리도 향상** (다른 Tier 유사도 0.75 → 0.65), **같은 Tier 응집도 향상** (0.89 → 0.91)
     - 강남구(TELECOM_ONLY) top-5: 동작 0.899 · 강북 0.897 · 광진 0.893 · 강동 0.889 · 용산 0.888 — 전부 TELECOM_ONLY 22구 내에서 매칭, Tier 경계가 임베딩 공간에 반영됨
  6. 회귀 검증: `run_tests.py` 6/6 PASS + `smoke_cortex_helpers.py` 17/17 PASS 재실행 확인
- **권장 후속 작업 (본 이슈 범위 외):**
  1. `@st.cache_data(ttl=3600)` 적용 위치: `src/app/cortex.py` 4 공개 함수 (#28 Streamlit 시점에서 wrapping)
  2. `gh issue edit 27 --body-file 00_issue.md` — finish-issue 단계에서 1회 동기화 (stale `mistral-large2`/`e5-base-v2` 표기 제거)
  3. dev_spec.md B4 AI_EMBED 섹션 L1710~1750 예시 코드가 `UPDATE RICHGO_MARKET_PRICE SET EMBEDDING=...` 패턴 — Marketplace read-only 불변식 위반. 별도 hotfix 또는 #40 후속으로 분리 처리 권장
- **AC 최종:** 4/4 PASS + AC-05 권고(AI_AGG TC-06 통해 커버됨) + SP Tier-aware 품질 개선 1건

### 2026-04-09 — /simplify 3-agent 리뷰 + 정리 패스
3개 리뷰 에이전트 병렬 (reuse / quality / efficiency). 실 버그/개선 5건 처리, scope creep 제안 다수 deferred.
- **`001_cortex_ai_insights.sql`** — `mart_with_richgo` CTE 삭제. MART에 이미 `AVG_MEME_PRICE` 컬럼 있음에도 V_RICHGO + V_BJD_DISTRICT_MAP을 correlated subquery로 재집계 중이었음 (003은 이미 올바르게 `m.AVG_MEME_PRICE` 직접 사용). 850행 × Marketplace 재JOIN 비용 제거 + 의존성 단순화.
- **`001`, `002`, `003` 공통** — 파일 상단에 "⚠ 비용 주의: 뷰 SELECT마다 AI 호출 / WHERE (CITY_CODE, STANDARD_YEAR_MONTH) 필터 필수 / SELECT * 금지" 경고 헤더 추가.
- **`002_cortex_ai_classify.sql`** — `YOY_PCT` 계산이 SELECT 프로젝션과 AI_CLASSIFY 프롬프트 양쪽에 중복되어 drift 위험. `with_yoy` 단일 CTE로 통합.
- **`003_cortex_ai_embed.sql`** — 전환기용 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS PROFILE_YM` 삭제. 본 이슈가 첫 커밋이라 새 배포는 CREATE 단일 경로만 존재, ALTER는 dead code.
- **`src/app/cortex.py`** — 미사용 `MULTI_SOURCE_CITIES` 상수 삭제 (Tier 분류는 `MART.DATA_TIER` 컬럼에서 직접 온다, 주석 보강). `_validate_year_month`: `None`/`isascii`/월 1-12 범위 체크 추가 (기존 `isdigit`은 fullwidth `２０２４１２` 통과 위험).
- **`sql/cortex/.ai.md`** — 의존성 목록 업데이트 (RICHGO/BJD 제거, MART 단일 의존).
- **회귀 재검증:**
  - 재배포: `T_DISTRICT_EMBEDDINGS refreshed (multi_ym=202412, telecom_ym=202604, rows=25)` 동일 결과
  - `run_tests.py` TC-01~06 **PASS 6/0** (`run_tests.log`)
  - `smoke_cortex_helpers.py` **PASS 19/0** (Pure Python 13 + Runtime 6) — 경계 케이스 3건(`202413`, `202400`, `２０２４１２`) 추가 거부 확인
- **Deferred (scope creep / 후속 대상):**
  - DataTier/DemandGrade StrEnum 도입 (#28 Streamlit 통합 시)
  - AI 결과 캐시 테이블 `T_AI_*_CACHE` + 월간 TASK (별도 이슈)
  - `WHEN NOT MATCHED BY SOURCE THEN DELETE` (Seoul 25구 안정, 리스크 낮음)
  - `V_AI_DISTRICT_FULL` 결합 뷰 (Streamlit 호출 round-trip 절감, #28 시점)
  - dev_spec.md B4 L1711~1757 `ALTER/UPDATE RICHGO` 예시 정정 (Marketplace 불변식 위반, 별도 hotfix)
- **다음 단계:** `/finish-issue 27`

### 2026-04-08 — /ri 복구 스냅샷 (세션 튕김 후)
- 브랜치: `feat/000027-cortex-ai-functions` · 이전 이후 신규 커밋 0건 (모두 미커밋 상태)
- 단계: **구현 중 (Green 검증 대기)** — 산출물은 전부 디스크에 존재하나 Snowflake 실행 검증 증거 없음
- 현재 디스크 산출물 (563 라인 / 전부 untracked):
  - `sql/cortex/.ai.md` — 디렉토리 목적·Dual-Tier 원칙·함수 네임스페이스 불변식
  - `sql/cortex/001_cortex_ai_insights.sql` (128 L) — `V_AI_DISTRICT_INSIGHTS` + `V_AI_STATE_SUMMARY` (AI_COMPLETE + AI_AGG, DATA_TIER CASE 분기)
  - `sql/cortex/002_cortex_ai_classify.sql` (69 L) — `V_AI_DEMAND_GRADE` (AI_CLASSIFY 짧은 라벨 3종, `:labels[0]::STRING`)
  - `sql/cortex/003_cortex_ai_embed.sql` (157 L) — `T_DISTRICT_EMBEDDINGS`(VECTOR(FLOAT,1024)) + `SP_REFRESH_DISTRICT_EMBEDDINGS` + `SP_FIND_SIMILAR_DISTRICTS` + 말미 CALL 초기 로드
  - `sql/test/test_12_cortex_ai.sql` (56 L) — TC-01~TC-06 Red/Green
  - `src/app/.ai.md` — Streamlit 루트 목적·공개 API 표·보안 불변식
  - `src/app/cortex.py` (153 L) — 4 공개 함수(`get_district_insight` / `classify_demand` / `find_similar_districts` / `aggregate_state_summary`) + TypedDict + allowlist(25구) + bind 파라미터
- 미완료 항목:
  - Snowflake MCP 연결 끊김(`proofKey` 에러) → V0 사전검증 7건 + `sql/cortex/` 3파일 실행 + TC-01~06 Green 확인 미수행
  - `CALL SP_REFRESH_DISTRICT_EMBEDDINGS()` 25행 초기 로드 미확인
  - PR 본문용 AI_COMPLETE 실행 시간/비용 추정(R3 완화 증거) 미측정
- 다음 액션 (우선순위 순):
  1. Snowflake MCP 재연결 (사용자 액션 필요) → `/restart`에 준하는 설정 확인
  2. `sql/cortex/001 → 002 → 003` 순서대로 실행 + `CALL SP_REFRESH_DISTRICT_EMBEDDINGS()`
  3. `sql/test/test_12_cortex_ai.sql` TC-01~TC-06 Green 확인
  4. `finish-issue` 전 `gh issue edit 27 --body-file 00_issue.md` 로 stale 모델명(`mistral-large2`/`e5-base-v2`) → `claude-4-sonnet`/`snowflake-arctic-embed-l-v2.0` 동기화
