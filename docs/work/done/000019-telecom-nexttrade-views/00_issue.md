# feat: 아정당 + NextTrade 참조 뷰 생성

## 목적
통신 계약(이사 시그널) + 주식 시세 데이터를 접근 가능하게 한다.

## 완료 기준
- [ ] `V_TELECOM_CONTRACT_STATS` 뷰 (V01 월별 지역 계약)
- [ ] `V_TELECOM_NEW_INSTALL` 뷰 (V05 신규 설치 — 이사 프록시 핵심)
- [ ] `V_TELECOM_BUNDLE` 뷰 (V02 번들 패턴)
- [ ] `V_TELECOM_FUNNEL` 뷰 (V03 계약 퍼널)
- [ ] `V_NEXTTRADE_REFER` 뷰 (종목 참조 A0)
- [ ] `V_NEXTTRADE_PRICE` 뷰 (체결가 A3)

## 테스트 코드 (TDD — 먼저 작성)

\`\`\`sql
-- test_04_telecom_nexttrade.sql
-- TC-01: 핵심 뷰 V05 존재 + row count > 0
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL;
-- EXPECTED: cnt > 0

-- TC-02: V05 필수 컬럼 확인
SELECT YEAR_MONTH, INSTALL_STATE, INSTALL_CITY, CONTRACT_COUNT, OPEN_COUNT, PAYEND_COUNT
FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL LIMIT 1;
-- EXPECTED: 6개 컬럼 모두 존재

-- TC-03: V01 존재
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_TELECOM_CONTRACT_STATS;
-- EXPECTED: cnt > 0

-- TC-04: NextTrade 종목 참조 존재
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_NEXTTRADE_REFER;
-- EXPECTED: cnt > 0

-- TC-05: NextTrade 체결가 필수 컬럼
SELECT DWDD, ISU_CD, TD_PRC, TRD_QTY, ACC_TRVAL
FROM MOVING_INTEL.ANALYTICS.V_NEXTTRADE_PRICE LIMIT 1;
-- EXPECTED: 5개 컬럼 존재

-- TC-06: 아정당 YEAR_MONTH 타입 확인
SELECT TYPEOF(YEAR_MONTH) AS tp FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL LIMIT 1;
-- EXPECTED: tp = 'DATE'
\`\`\`

## 참조
- `docs/specs/dev_spec.md` A1-6~A1-7 (아정당/NextTrade 스키마)
- 원본 아정당: `SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS`
- 원본 NextTrade: `NEXTRADE_EQUITY_MARKET_DATA.FIN`
- 의존성: #16 (DB/스키마)

## 불변식
- 아정당은 시/도 + 시/군/구 단위 (동 단위 아님)
- V05 OPEN_COUNT가 이사 프록시의 핵심 시그널
- NextTrade는 시간축 조인만 (행정동 조인 없음)
## 작업 내역
- [x] sql/test/test_04_telecom_nexttrade.sql 생성 (TC-01~TC-07)
- [x] sql/views/004_telecom_nexttrade_views.sql 생성 (V_TELECOM_NEW_INSTALL, V_TELECOM_CONTRACT_STATS, V_TELECOM_BUNDLE, V_TELECOM_FUNNEL, V_NEXTTRADE_REFER, V_NEXTTRADE_PRICE)
- [x] sql/views/.ai.md 생성
- [x] sql/test/.ai.md 최신화
- [x] sql/.ai.md 최신화 (2026-04-07 worker-3 교차 검증 완료)
