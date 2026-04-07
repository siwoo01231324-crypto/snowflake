-- ============================================================
-- 001_create_database_schema.sql
-- 프로젝트 전용 데이터베이스 및 스키마 생성
-- 이슈: #16 (feat: 프로젝트 DB/스키마 생성 + 웨어하우스 검증)
-- 멱등성: IF NOT EXISTS 사용 — 반복 실행 안전
-- ============================================================

-- Step 1: 웨어하우스 사용 선언
USE WAREHOUSE MOVING_INTEL_WH;

-- Step 2: 프로젝트 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS MOVING_INTEL
  COMMENT = '무빙 인텔리전스 프로젝트 전용 데이터베이스';

-- Step 3: 분석 스키마 생성
CREATE SCHEMA IF NOT EXISTS MOVING_INTEL.ANALYTICS
  COMMENT = 'Marketplace 데이터 기반 분석 뷰/UDF 저장 스키마';
