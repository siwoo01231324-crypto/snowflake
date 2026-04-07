# 구현 계획: 아정당 + NextTrade 참조 뷰 6개 생성

## AC 체크리스트
- [x] V_TELECOM_CONTRACT_STATS 뷰 (V01 월별 지역 계약)
- [x] V_TELECOM_NEW_INSTALL 뷰 (V05 신규 설치 — 이사 프록시 핵심)
- [x] V_TELECOM_BUNDLE 뷰 (V02 번들 패턴) — SELECT *, 컬럼 확인 필요
- [x] V_TELECOM_FUNNEL 뷰 (V03 계약 퍼널) — SELECT *, 컬럼 확인 필요
- [x] V_NEXTTRADE_REFER 뷰 (종목 참조 A0)
- [x] V_NEXTTRADE_PRICE 뷰 (체결가 A3)

## 구현 계획
1. TDD Red: `sql/test/test_04_telecom_nexttrade.sql` 작성 (TC-01~TC-07)
2. V02/V03 소스 테이블 스키마 탐색 (dev_spec에 없음)
3. TDD Green: `sql/views/004_telecom_nexttrade_views.sql` 작성 (6개 뷰)
4. `.ai.md` 최신화 (sql/, sql/views/, sql/test/)
5. Snowflake에서 테스트 실행 → Red→Green 확인
6. 커밋

## 작업 내역

### 2026-04-07

#### 1. TDD Red — 테스트 쿼리 작성
- 파일: `sql/test/test_04_telecom_nexttrade.sql`
- TC-01: V_TELECOM_NEW_INSTALL row count > 0
- TC-02: V05 필수 컬럼 6개 존재 (YEAR_MONTH, INSTALL_STATE, INSTALL_CITY, CONTRACT_COUNT, OPEN_COUNT, PAYEND_COUNT)
- TC-03: V_TELECOM_CONTRACT_STATS row count > 0
- TC-04: V_NEXTTRADE_REFER row count > 0
- TC-05: V_NEXTTRADE_PRICE 필수 컬럼 5개 (DWDD, ISU_CD, TD_PRC, TRD_QTY, ACC_TRVAL)
- TC-06: V_TELECOM_BUNDLE row count > 0
- TC-07: V_TELECOM_FUNNEL row count > 0

#### 2. TDD Green — 뷰 SQL 작성
- 파일: `sql/views/004_telecom_nexttrade_views.sql`
- 기존 패턴 참조: `002_richgo_views.sql` (#17)

**아정당 뷰 4개:**
| 뷰 이름 | 원본 테이블 | 주요 컬럼 | SELECT 방식 |
|---------|------------|----------|------------|
| V_TELECOM_NEW_INSTALL | V05_REGIONAL_NEW_INSTALL | YEAR_MONTH, INSTALL_STATE/CITY, CONTRACT/OPEN/PAYEND_COUNT, BUNDLE/STANDALONE_COUNT, AVG_NET_SALES | 명시적 9컬럼 |
| V_TELECOM_CONTRACT_STATS | V01_MONTHLY_REGIONAL_CONTRACT_STATS | 위 + MAIN_CATEGORY_NAME, CONSULT_REQUEST_COUNT, OPEN/PAYEND_CVR, TOTAL_NET_SALES | 명시적 12컬럼 |
| V_TELECOM_BUNDLE | V02_REGIONAL_BUNDLE_STATS | dev_spec에 스키마 없음 | SELECT * (TODO) |
| V_TELECOM_FUNNEL | V03_REGIONAL_CONTRACT_FUNNEL | dev_spec에 스키마 없음 | SELECT * (TODO) |

- 원본 DB: `SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS`
- 불변식: 아정당은 시/도 + 시/군/구 단위 (동 단위 아님), V05 OPEN_COUNT가 이사 프록시 핵심

**NextTrade 뷰 2개:**
| 뷰 이름 | 원본 테이블 | 주요 컬럼 | 비고 |
|---------|------------|----------|------|
| V_NEXTTRADE_REFER | NX_HT_BAT_REFER_A0 | DWDD, ISU_CD, ISU_SRT_CD, ISU_ABWD_NM, ISU_ENAW_NM, IND_ID, BASE_PRC, LSST_CT, CAPT_AMT | 종목 참조 단독 뷰 |
| V_NEXTTRADE_PRICE | NX_HT_ONL_MKTPR_A3 JOIN NX_HT_BAT_REFER_A0 | p.DWDD, p.ISU_CD, r.ISU_ABWD_NM, r.IND_ID, 시가/고가/저가/체결가, 거래량, 거래대금 | A3+A0 JOIN (ISU_CD, DWDD) |

- 원본 DB: `NEXTRADE_EQUITY_MARKET_DATA.FIN`
- 불변식: NextTrade는 시간축 조인만 (행정동 조인 없음)
- 모든 뷰: `CREATE OR REPLACE VIEW` + `COMMENT` — 멱등성 보장

#### 3. .ai.md 최신화
- `sql/.ai.md` — views/ 디렉토리 설명 추가
- `sql/views/.ai.md` — 신규 생성 (004_telecom_nexttrade_views.sql 항목)
- `sql/test/.ai.md` — test_04_telecom_nexttrade.sql 항목 추가
- `docs/work/active/000019-telecom-nexttrade-views/00_issue.md` — 작업 내역 기록

#### 4. 미완료 항목
- [ ] Snowflake 실행: V02/V03 소스 테이블 실제 존재 + 컬럼 확인 (`SHOW TABLES LIKE 'V02%'`, `SHOW TABLES LIKE 'V03%'`)
- [ ] V02/V03 뷰를 `SELECT *` → 명시적 컬럼 SELECT로 교체
- [ ] Snowflake 실행: `004_telecom_nexttrade_views.sql` → `test_04_telecom_nexttrade.sql` 순서로 실행하여 Red→Green 확인
