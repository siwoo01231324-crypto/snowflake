-- ============================================================
-- 002_add_move_signal_index.sql
-- MART_MOVE_ANALYSIS에 MOVE_SIGNAL_INDEX 컬럼 추가 마이그레이션
-- 이슈: #22
-- ============================================================
-- 실행 방법: features/move_signal.py update_mart_with_signal_index() 호출 후 이 스크립트 실행 불필요
-- (Snowpark overwrite 방식으로 마트 전체 재작성)
-- 단독 실행 시: ALTER → Python SP 호출 순서로 진행

USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

-- 컬럼이 없을 때만 추가 (이미 존재하면 SKIP)
ALTER TABLE MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
  ADD COLUMN IF NOT EXISTS MOVE_SIGNAL_INDEX FLOAT;

ALTER TABLE MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
  ADD COLUMN IF NOT EXISTS CARRYOVER_RATIO FLOAT;

-- 컬럼 추가 확인
SHOW COLUMNS IN TABLE MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS;
