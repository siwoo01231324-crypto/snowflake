# Snowflake 핵심 기능 및 해커톤 활용 전략

> Snowflake AI & Data Hackathon 2026 Korea 테크트랙 대비 — Snowflake 플랫폼 기능 분석 및 가산점 확보 전략

## Executive Summary

Snowflake는 단순 데이터 웨어하우스를 넘어 **AI/ML 통합 플랫폼**으로 진화했다. 2025~2026년 사이 Cortex AI 전 기능이 GA(Generally Available) 상태에 도달했으며, Cortex Agents, Cortex Code, Cortex Search 등 에이전트 기반 기능이 대거 추가되었다. 해커톤 평가기준에서 **"Snowflake 활용도"가 가산점 항목**이므로, 가능한 한 많은 Snowflake 네이티브 기능을 조합해 활용하는 것이 수상 전략의 핵심이다.

본 문서는 해커톤에서 실질적으로 활용 가능한 Snowflake 기능을 분류하고, 각 기능별 해커톤 활용 시나리오와 가산점 확보 전략을 제시한다.

---

## 목차

1. [Cortex AI LLM Functions](#1-cortex-ai-llm-functions)
2. [Cortex Search (RAG 기반 검색)](#2-cortex-search-rag-기반-검색)
3. [Cortex Analyst (자연어 → SQL)](#3-cortex-analyst-자연어--sql)
4. [Cortex Agents (멀티툴 에이전트)](#4-cortex-agents-멀티툴-에이전트)
5. [Cortex Fine-tuning (모델 미세조정)](#5-cortex-fine-tuning-모델-미세조정)
6. [Cortex Code (AI 코딩 에이전트)](#6-cortex-code-ai-코딩-에이전트)
7. [Snowpark (Python/Java/Scala ML)](#7-snowpark-pythonjavascala-ml)
8. [Streamlit in Snowflake (데이터 앱 UI)](#8-streamlit-in-snowflake-데이터-앱-ui)
9. [Arctic LLM & Arctic Embed](#9-arctic-llm--arctic-embed)
10. [Snowflake Marketplace](#10-snowflake-marketplace)
11. [VECTOR 데이터 타입](#11-vector-데이터-타입)
12. [가산점 극대화 전략](#12-가산점-극대화-전략)
13. [추천 기능 조합 아키텍처](#13-추천-기능-조합-아키텍처)

---

## 1. Cortex AI LLM Functions

### 개요

Snowflake Cortex AI Functions는 SQL 쿼리 내에서 직접 LLM을 호출할 수 있는 서버리스 함수 집합이다. 별도 인프라 구축 없이 SQL `SELECT` 문에서 바로 AI 기능을 사용할 수 있다는 점이 핵심 차별점이다.

**상태**: GA (Generally Available)

### 주요 함수 목록

| 함수명 | 용도 | 컨텍스트 윈도우 | 비고 |
|--------|------|-----------------|------|
| **AI_COMPLETE** | 텍스트/이미지 기반 LLM 완성 | 모델별 상이 | Claude 4.6 Sonnet, GPT, Llama, Mistral 등 지원 |
| **AI_CLASSIFY** | 텍스트/이미지를 사용자 정의 카테고리로 분류 | - | 최대 500개 카테고리 |
| **AI_FILTER** | True/False 필터링 (WHERE/JOIN 절 활용) | - | 행 단위 AI 필터링 |
| **AI_EXTRACT** | 구조화된 정보 추출 (다국어 지원) | 128,000 토큰 | Arctic-extract 모델 기반 |
| **AI_SENTIMENT** | 감성 분석 (-1 ~ +1 스케일) | 2,048 토큰 | 간단한 감성 점수 반환 |
| **AI_AGG** | 다중 행 집계 인사이트 | 제한 없음 | 컨텍스트 윈도우 제한 없이 집계 |
| **AI_SUMMARIZE_AGG** | 다중 행 요약 | 제한 없음 | 최대 8,192 토큰 출력 |
| **AI_EMBED** | 벡터 임베딩 생성 | 모델별 상이 | Arctic Embed, E5, Voyage 등 |
| **AI_SIMILARITY** | 의미적 유사도 계산 | - | 임베딩 기반 |
| **AI_TRANSLATE** | 다국어 번역 | 4,096 토큰 | |
| **AI_REDACT** | PII 제거 | - | 개인정보 마스킹 |
| **AI_TRANSCRIBE** | 음성/영상 → 텍스트 변환 | - | 타임스탬프, 화자 식별 지원 |
| **AI_PARSE_DOCUMENT** | 문서 OCR 및 레이아웃 추출 | - | 페이지당 약 970 토큰 |
| **AI_COUNT_TOKENS** | 토큰 수 계산 | - | 모델 제한 초과 방지용 |

**레거시 함수** (하위 호환): `COMPLETE`, `SUMMARIZE`, `EXTRACT_ANSWER`, `EMBED_TEXT_768`, `EMBED_TEXT_1024` — 신규 프로젝트에서는 `AI_*` 시리즈 사용 권장.

**보안**: Cortex Guard (Meta Llama Guard 3 기반) 옵션으로 unsafe 응답 필터링 가능.

### 해커톤 활용 시나리오

- **주식 뉴스 감성 분석**: `AI_SENTIMENT`로 종목 관련 뉴스/리뷰 감성 점수 산출 → 주가 변동과 상관 분석
- **부동산 리뷰 요약**: `AI_SUMMARIZE_AGG`로 단지별 리뷰 집계 요약
- **CS 통화 분석**: `AI_TRANSCRIBE`로 음성 데이터 텍스트화 → `AI_CLASSIFY`로 문의 유형 자동 분류
- **다국어 데이터 통합**: `AI_TRANSLATE`로 영문 데이터를 한국어로 변환하여 통합 분석
- **개인정보 처리**: `AI_REDACT`로 고객 데이터 내 PII 자동 제거 → 컴플라이언스 시연

---

## 2. Cortex Search (RAG 기반 검색)

### 개요

Cortex Search는 비정형 데이터에 대한 **시맨틱 검색 서비스**로, RAG(Retrieval-Augmented Generation) 파이프라인의 핵심 구성요소다. 2026년 3월 GA 업데이트에서 다중 검색 컬럼 지원이 추가되었다.

**상태**: GA (2026-03 다중 컬럼 업데이트)

### 핵심 기능

- **다중 검색 컬럼 (Multi-Index)**: 단일 서비스에서 복수 컬럼을 검색 가능. TEXT INDEX(키워드/렉시컬 검색)와 VECTOR INDEX(시맨틱 검색)를 혼합 구성 가능
- **인덱스별 부스트 (Index-Specific Boosts)**: 검색 가중치를 애플리케이션 레이어에서 동적으로 제어. 사용자 의도와 비즈니스 요구에 따라 검색 동작을 실시간 변경 가능
- **동적 필터**: 각 검색 호출마다 속성 컬럼 기반 필터 조건 적용 가능
- **서비스 선택**: 도구 설명 기반으로 단일 검색 서비스를 자동 선택하여 레이턴시/비용 절감

### 해커톤 활용 시나리오

- **부동산 문서 RAG**: 아파트 단지 정보, 시세 리포트 등을 Cortex Search로 인덱싱 → 자연어 질의로 "강남 3룸 10억 이하 아파트" 검색
- **CS 상담 내역 검색**: 아정당 CS 운영 데이터를 시맨틱 검색으로 유사 문의 사례 자동 추천
- **뉴스/리포트 RAG**: 주식 시장 관련 비정형 텍스트 데이터에 대한 RAG 기반 Q&A 시스템 구축

---

## 3. Cortex Analyst (자연어 → SQL)

### 개요

Cortex Analyst는 자연어 질의를 SQL로 변환하는 완전 관리형 서비스다. 시맨틱 모델(YAML)을 통해 비즈니스 용어와 DB 스키마 간 브릿지를 제공하여 SQL을 모르는 사용자도 데이터를 조회할 수 있다.

**상태**: GA
**기반 모델**: Mistral, Meta LLM (자동 선택), Claude Sonnet, GPT 4.1, Arctic Text2SQL R1.5도 활용 가능

### 핵심 기능

- **시맨틱 뷰 (Semantic View)**: 논리적 테이블, 디멘션, 팩트, 메트릭, 조인 관계를 YAML로 정의
- **REST API**: 토큰 기반 인증, 멀티턴 대화 지원 (대화 히스토리 전달)
- **RBAC 통합**: Snowflake 거버넌스 내에서 데이터 접근 제어 유지
- **통합 가능**: Slack, Teams, Streamlit 등 기존 도구에 임베딩 가능

### 한계

- 이전 SQL 쿼리 결과 참조 불가
- SQL로 답변 가능한 질문에 제한
- 긴 대화나 빈번한 의도 전환에 취약

### 해커톤 활용 시나리오

- **셀프서비스 분석 인터페이스**: 4종 데이터셋에 대한 시맨틱 모델 정의 → 심사위원이 자연어로 직접 데이터 조회하는 데모
- **Streamlit 연동**: Streamlit 앱에서 Cortex Analyst 호출 → 자연어 입력 → 차트 자동 생성
- **크로스 데이터셋 질의**: "서초구 유동인구가 가장 많은 시간대의 카드 소비 패턴은?" 같은 복합 질의

---

## 4. Cortex Agents (멀티툴 에이전트)

### 개요

Cortex Agents는 Snowflake 네이티브 AI 에이전트로, 구조화/비구조화 데이터를 오케스트레이션하여 복합적인 질의에 자율적으로 답변한다. 2025년 11월 GA 달성.

**상태**: GA (2025-11)
**지원 모델**: Claude 4.6 Sonnet, Claude Sonnet 4.5, OpenAI GPT-4.1, claude-haiku-4-5(preview) 등

### 아키텍처 (4단계 워크플로)

1. **Planning**: 요청 파싱, 태스크 분할, 도구 라우팅
2. **Tool Use**: Cortex Analyst(정형 데이터), Cortex Search(비정형 데이터), Custom Tools(저장 프로시저/UDF), Web Search(Brave API) 활용
3. **Reflection**: 도구 실행 결과 평가, 추가 반복 또는 최종 응답 결정
4. **Monitor & Iterate**: 메트릭 수집, 피드백 반영

### 핵심 기능

- **Agent Object**: 설정 메타데이터, 오케스트레이션 설정, 도구 상세를 저장하는 재사용 가능 객체
- **Threads**: 대화 컨텍스트를 서버사이드에서 영속적으로 관리
- **Custom Tools**: 저장 프로시저 및 UDF를 에이전트 도구로 연결
- **Web Search**: Brave API 통합 실시간 웹 검색

### 해커톤 활용 시나리오 (핵심 추천)

- **통합 데이터 에이전트**: 4종 데이터셋(주식/부동산/지역빅데이터/통신)을 Cortex Analyst + Cortex Search로 연결한 멀티툴 에이전트 구축
- **투자 자문 에이전트**: 주식 데이터 조회(Analyst) + 부동산 시세 검색(Search) + 웹 뉴스(Web Search)를 조합한 종합 투자 자문
- **고객 인사이트 에이전트**: 통신 고객 세그먼트 분석 + 지역 소비 패턴 + 유동인구 데이터를 통합 분석하는 마케팅 에이전트

> **가산점 전략**: Cortex Agents는 Cortex Analyst, Cortex Search, Custom Tools를 모두 결합하므로 단일 기능으로 **가장 많은 Snowflake 기능을 동시에 활용**할 수 있는 최적의 선택이다.

---

## 5. Cortex Fine-tuning (모델 미세조정)

### 개요

Cortex Fine-tuning은 사전 훈련된 LLM을 도메인 특화 태스크에 맞게 미세조정하는 서버리스 기능이다. PEFT(Parameter-Efficient Fine-Tuning) 방식으로 경량 어댑터를 생성한다.

**상태**: GA (2025-02)

### 핵심 기능

- **UI 및 SQL 지원**: Cortex AI Studio(UI) 또는 `FINETUNE()` SQL 함수로 실행
- **학습 데이터**: Snowflake 테이블/뷰에서 `prompt`와 `completion` 컬럼으로 제공
- **하이퍼파라미터**: `max_epochs` (1~10) 설정 가능
- **모델 공유**: Fine-tuned 모델을 Data Sharing을 통해 다른 계정과 공유 가능
- **Arctic-extract 미세조정**: 문서 추출 모델 특화 Fine-tuning 지원

### 해커톤 활용 시나리오

- **도메인 특화 분류기**: 부동산 매물 설명 → 투자 등급 분류 모델 Fine-tuning
- **CS 자동응답**: 아정당 CS 데이터로 고객 문의 자동 응답 모델 학습
- **주식 시그널 해석**: 주식 데이터 패턴에 대한 자연어 해석 모델 Fine-tuning

> **주의**: 해커톤 기간(수일)에 Fine-tuning까지 시도하면 시간이 부족할 수 있다. 보조 기능으로 활용하되, 핵심 파이프라인은 Pre-trained 모델 기반으로 구성하는 것이 안전하다.

---

## 6. Cortex Code (AI 코딩 에이전트)

### 개요

Cortex Code는 Snowflake 네이티브 AI 코딩 에이전트로, 자연어로 SQL/Python 코드를 생성·수정·최적화하며, 엔터프라이즈 데이터 컨텍스트를 이해한다. 2026년 2월 발표.

**상태**: GA (Snowsight), CLI도 지원 (Windows 네이티브 포함)

### 핵심 기능

- **코드 생성/수정/최적화/설명**: 대화형 인터페이스로 SQL/Python 작업
- **Diff View**: AI 제안 변경사항을 적용 전 미리보기
- **원클릭 쿼리 수정**: 실패한 쿼리를 한 번의 클릭으로 수정
- **Agent Teams**: 복수 서브에이전트를 병렬로 실행하는 멀티에이전트 오케스트레이터
- **인라인 코드 제안**: 컨텍스트 인식 자동 완성

### 해커톤 활용 시나리오

- **개발 생산성**: 해커톤 기간 중 Cortex Code로 빠른 SQL/Python 코드 생성 → 개발 속도 극대화
- **데모 시 언급**: 개발 과정에서 Cortex Code 활용 사실을 데모 영상에 포함하여 Snowflake 활용도 가산점 확보

> **참고**: Cortex Code는 개발 도구이므로 최종 프로덕트의 기능보다는 개발 프로세스에서의 활용을 강조하는 것이 적절하다.

---

## 7. Snowpark (Python/Java/Scala ML)

### 개요

Snowpark는 Snowflake 내에서 Python, Java, Scala로 데이터 처리 및 ML 워크로드를 실행할 수 있는 개발자 프레임워크다. DataFrame API, UDF/UDTF/UDAF, 저장 프로시저를 지원한다.

**상태**: GA

### 핵심 기능

- **DataFrame API**: Pandas와 유사한 인터페이스로 Snowflake 데이터 조작 (lazy evaluation)
- **UDF/UDTF/UDAF**: Python/Java/Scala로 커스텀 함수 작성 후 SQL에서 호출
- **ML Jobs**: Python 3.11/3.12 지원, 클라이언트 Python 버전에 맞는 런타임 자동 선택
- **모델 레지스트리**: ML 모델 등록, 버전 관리, 배포
- **Feature Store**: 피처 스냅샷 관리
- **Snowpark Container Services (SPCS)**: GPU 기반 컨테이너 워크로드 실행

### 2026년 최신 업데이트

- DataFrame.join 쿼리 최적화 (중복 alias 제거)
- `DECFLOAT` 데이터 타입 지원 (38자리 정밀도)
- `array_union_agg` 함수 추가
- `preserve_parameter_names` 플래그 추가 (UDF/저장 프로시저)

### 해커톤 활용 시나리오

- **ML 파이프라인**: Snowpark Python으로 데이터 전처리 → 모델 학습 → 예측 파이프라인 구축 (데이터가 Snowflake를 떠나지 않음)
- **커스텀 UDF**: 주가 변동 예측 모델을 UDF로 래핑 → SQL에서 직접 호출
- **피처 엔지니어링**: 4종 데이터셋의 크로스 조인 피처를 Snowpark DataFrame으로 생성

---

## 8. Streamlit in Snowflake (데이터 앱 UI)

### 개요

Streamlit in Snowflake(SiS)는 Snowflake 내에서 직접 실행되는 완전 관리형 Streamlit 앱 호스팅 서비스다. 별도 서버 없이 데이터 앱을 빠르게 프로토타이핑할 수 있다.

**상태**: GA (컨테이너 런타임 2026-03 GA)

### 핵심 기능

- **컨테이너 런타임 (2026-03 GA)**: GPU 접근, 광범위한 Python 패키지 지원, 슬립 타이머 없는 장시간 실행
- **Secrets 관리**: 컨테이너 런타임 앱에서 Snowflake Secrets를 환경변수로 자동 매핑
- **앱 공유**: 앱 뷰어 URL을 통해 Snowsight 없이도 공유 가능
- **핫 리로딩**: 코드 변경 시 실시간 반영 → 빠른 프로토타이핑 (기존 대비 40% 빠른 개발)
- **통합**: Snowpark, UDF, 저장 프로시저, Native App Framework와 심리스 연동

### 해커톤 활용 시나리오 (핵심 추천)

- **데모 UI**: 해커톤 데모 영상에서 보여줄 인터랙티브 대시보드 구축
- **Cortex Agent 프론트엔드**: Streamlit 앱에서 Cortex Agent를 호출하는 챗봇 인터페이스
- **실시간 데이터 탐색**: 4종 데이터셋을 시각화하는 대시보드 (차트, 지도, 필터)
- **심사위원 체험**: 심사위원이 직접 앱을 조작하며 데이터를 탐색할 수 있는 인터랙티브 경험

> **가산점 전략**: Streamlit in Snowflake는 "Snowflake 플랫폼 내에서 전부 구현"이라는 메시지를 가장 직관적으로 전달하는 수단이다.

---

## 9. Arctic LLM & Arctic Embed

### Arctic LLM

Snowflake가 자체 개발한 오픈소스 LLM (Apache 2.0 라이선스).

- **아키텍처**: Dense-MoE Hybrid Transformer (총 480B 파라미터, 활성 17B)
- **특화 분야**: SQL 생성, 코딩, 명령어 수행
- **효율성**: $2M 미만 학습 비용 (3K GPU 주 미만)
- **Cortex AI 통합**: `AI_COMPLETE` 함수에서 모델로 선택 가능

### Arctic Embed

텍스트 임베딩 모델 패밀리 (5종, Apache 2.0).

- **모델 범위**: 23M ~ 334M 파라미터
- **성능**: 334M 모델이 1B+ 모델과 동등한 검색 성능 달성
- **Arctic Embed 2.0 (2024-12)**: 다국어 지원, 8,192 토큰 컨텍스트
- **Cortex AI 통합**: `AI_EMBED` 함수에서 모델로 선택 가능

### 해커톤 활용 시나리오

- **Snowflake 자체 모델 활용**: Arctic LLM/Embed 사용 시 "Snowflake 생태계 완전 활용" 메시지 전달 → 가산점 유리
- **비용 효율적 RAG**: Arctic Embed 2.0으로 한국어 데이터 임베딩 → Cortex Search와 결합
- **SQL 생성**: Arctic의 SQL 특화 능력을 활용한 Text-to-SQL 파이프라인

---

## 10. Snowflake Marketplace

### 개요

Snowflake Marketplace는 670개 이상 제공자의 2,700개 이상 리스팅(데이터셋, API, 네이티브 앱, AI 제품)에 접근할 수 있는 데이터 마켓플레이스다.

**상태**: GA

### 핵심 기능

- **즉시 쿼리 가능**: 데이터 변환 없이 계정 내에서 바로 조회
- **자사 데이터와 조인**: 마켓플레이스 데이터와 내부 데이터를 직접 결합
- **도메인 다양성**: AI/ML, 금융, 의료, 지리공간 등

### 해커톤 활용 시나리오

- **해커톤 제공 데이터셋 접근**: NextTrade, RICHGO, SPH, 아정당 4종 데이터셋이 Marketplace를 통해 제공
- **보조 데이터 확보**: 날씨 데이터, 경제 지표 등 추가 외부 데이터를 Marketplace에서 확보하여 분석 강화
- **데이터 결합 데모**: Marketplace 데이터와 제공 데이터의 조인을 통해 "Snowflake 데이터 공유 생태계" 활용을 시연

---

## 11. VECTOR 데이터 타입

### 개요

Snowflake 네이티브 VECTOR 데이터 타입으로 벡터 임베딩을 테이블에 직접 저장하고 유사도 검색을 수행할 수 있다.

**상태**: GA

### 핵심 기능

- **데이터 타입**: `VECTOR(FLOAT, <차원>)` — 최대 4,096차원
- **유사도 함수**:
  - `VECTOR_COSINE_SIMILARITY` — 코사인 유사도
  - `VECTOR_INNER_PRODUCT` — 내적
  - `VECTOR_L1_DISTANCE` — L1 거리
  - `VECTOR_L2_DISTANCE` — L2 거리
- **Cortex AI 연동**: `AI_EMBED` → VECTOR 컬럼 저장 → 유사도 검색의 엔드투엔드 파이프라인

### 해커톤 활용 시나리오

- **종목 유사도 검색**: 주식 종목 설명을 임베딩하여 유사 종목 추천
- **아파트 유사도**: 아파트 단지 특성을 벡터화하여 유사 단지 검색
- **고객 클러스터링**: 통신 고객 세그먼트 데이터를 벡터화하여 유사 고객군 식별

---

## 12. 가산점 극대화 전략

### 평가 항목별 Snowflake 기능 매핑

| 평가 기준 | 관련 Snowflake 기능 | 전략 |
|-----------|---------------------|------|
| **기술혁신성** | Cortex Agents, Cortex Search (RAG), VECTOR | 멀티툴 에이전트 + RAG 파이프라인으로 최신 AI 아키텍처 시연 |
| **데이터활용능력** | Snowpark, Marketplace, AI Functions | 4종 데이터셋 크로스 조인 + 외부 데이터 결합 |
| **문제해결능력** | Cortex Analyst, Cortex Agents | 자연어 질의로 복합 비즈니스 문제 해결 시연 |
| **비즈니스임팩트** | Streamlit, Cortex Analyst | 비기술 사용자도 활용 가능한 UI + 셀프서비스 분석 |
| **Snowflake 활용도 (가산점)** | 전체 기능 최대 활용 | 아래 계층별 전략 참조 |

### 가산점 확보 계층 전략

**필수 (Tier 1 — 기본 가산점)**:
- Snowflake 데이터 웨어하우스 사용 (데이터 저장/조회)
- Snowpark Python으로 데이터 처리
- Streamlit in Snowflake로 UI 구축

**권장 (Tier 2 — 중급 가산점)**:
- Cortex AI Functions 활용 (AI_COMPLETE, AI_SENTIMENT 등)
- Cortex Analyst로 자연어 → SQL 인터페이스
- VECTOR 데이터 타입 + AI_EMBED로 시맨틱 검색

**차별화 (Tier 3 — 최대 가산점)**:
- Cortex Agents로 멀티툴 에이전트 구축
- Cortex Search로 RAG 파이프라인 구현
- Cortex Fine-tuning으로 도메인 특화 모델 생성
- Arctic LLM/Embed 활용으로 Snowflake 생태계 완전 활용
- Marketplace 외부 데이터 결합

---

## 13. 추천 기능 조합 아키텍처

### 최적 아키텍처: "Cortex Agent 중심 풀스택"

```
[사용자] → [Streamlit in Snowflake UI]
                    ↓
            [Cortex Agent]
           ↙      ↓       ↘
  [Cortex      [Cortex     [Custom Tools]
  Analyst]     Search]     (Snowpark UDF)
     ↓            ↓             ↓
  [정형 데이터]  [비정형 RAG]  [ML 모델 예측]
     ↓            ↓             ↓
  ← ← ← [Snowflake 데이터 웨어하우스] → → →
         (4종 데이터셋 + Marketplace)
              ↓
         [VECTOR 타입]
         [AI_EMBED로 임베딩]
```

### 활용 Snowflake 기능 체크리스트

- [ ] Snowflake 데이터 웨어하우스 (기본)
- [ ] Snowpark Python (데이터 처리 / ML)
- [ ] Streamlit in Snowflake (UI)
- [ ] Cortex AI Functions (AI_COMPLETE, AI_SENTIMENT, AI_EMBED 등)
- [ ] Cortex Analyst (자연어 → SQL)
- [ ] Cortex Search (RAG)
- [ ] Cortex Agents (멀티툴 오케스트레이션)
- [ ] VECTOR 데이터 타입 (벡터 검색)
- [ ] Arctic LLM / Arctic Embed (Snowflake 자체 모델)
- [ ] Marketplace (외부 데이터 결합)
- [ ] Cortex Fine-tuning (선택적 — 시간 여유 시)
- [ ] Cortex Code (개발 프로세스에서 활용)

> **목표**: 위 체크리스트에서 최소 8개 이상 기능을 활용하여 "Snowflake 플랫폼을 가장 깊이 있게 활용한 팀"이라는 인상을 심사위원에게 전달한다.

---

## 시사점 및 전략적 함의

1. **Cortex Agents가 핵심 허브**: 단일 기능으로 가장 많은 Snowflake 서비스(Analyst, Search, Custom Tools, Web Search)를 연결할 수 있어, 가산점 극대화의 최적 진입점이다.

2. **Streamlit in Snowflake는 필수**: 데모 영상(10분)에서 시각적 임팩트를 줄 수 있는 가장 효과적인 수단이며, 심사위원이 직접 체험 가능한 인터페이스를 제공한다.

3. **Arctic 생태계 활용은 차별화 포인트**: 대부분의 팀이 OpenAI/Claude 등 외부 모델을 사용할 것이므로, Snowflake 자체 모델(Arctic LLM, Arctic Embed)을 적극 활용하면 "Snowflake 활용도" 가산점에서 경쟁 우위를 확보할 수 있다.

4. **데이터셋 간 결합이 핵심 차별화**: 4종 데이터셋을 단독으로 사용하는 것보다 크로스 조인하여 새로운 인사이트를 도출하는 것이 "데이터 활용 능력" 점수를 높이는 핵심이다.

5. **Fine-tuning은 선택적**: 해커톤 기간의 제약을 고려하면 Fine-tuning은 시간이 허락할 때만 시도하고, 핵심 파이프라인은 Pre-trained 모델 기반으로 안정적으로 구축해야 한다.

---

## 출처

- [Snowflake Cortex AI LLM Functions 공식 문서](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- [Snowflake Cortex Analyst 공식 문서](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Snowflake AI/ML Features Overview](https://docs.snowflake.com/en/guides-overview-ai-features)
- [Snowflake Cortex Agents 공식 문서](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Cortex Agents GA 릴리스 노트 (2025-11-04)](https://docs.snowflake.com/en/release-notes/2025/other/2025-11-04-cortex-agents)
- [Cortex Search 업데이트 (2026-03-12 GA)](https://docs.snowflake.com/en/en/release-notes/2026/other/2026-03-12-recent-cortex-search)
- [Cortex Search Overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview)
- [Cortex Fine-tuning 공식 문서](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-finetuning)
- [Cortex Fine-tuning GA 릴리스 노트 (2025-02-07)](https://docs.snowflake.com/en/release-notes/2025/other/2025-02-07-cortex-finetuning)
- [Cortex Code 제품 페이지](https://www.snowflake.com/en/product/features/cortex-code/)
- [Cortex Code 공식 문서](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)
- [Cortex Code 발표 보도자료 (2026-02-03)](https://www.snowflake.com/en/news/press-releases/snowflake-unveils-cortex-code-an-ai-coding-agent-that-drastically-increases-productivity-by-understanding-your-enterprise-data-context/)
- [Snowpark API 공식 문서](https://docs.snowflake.com/en/developer-guide/snowpark/index)
- [Snowpark Python 2026 릴리스 노트](https://docs.snowflake.com/en/release-notes/clients-drivers/snowpark-python-2026)
- [Snowflake ML Python 2026 릴리스 노트](https://docs.snowflake.com/en/en/release-notes/clients-drivers/snowpark-ml-2026)
- [Streamlit in Snowflake 공식 문서](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Streamlit 컨테이너 런타임 GA (2026-03-09)](https://docs.snowflake.com/en/release-notes/2026/other/2026-03-09-sis-container-runtime-ga)
- [Snowflake Arctic 제품 페이지](https://www.snowflake.com/en/product/features/arctic/)
- [Snowflake Arctic Embed 소개 블로그](https://www.snowflake.com/en/blog/introducing-snowflake-arctic-embed-snowflakes-state-of-the-art-text-embedding-family-of-models/)
- [Arctic Embed 2.0 다국어 지원 블로그](https://www.snowflake.com/en/engineering-blog/snowflake-arctic-embed-2-multilingual/)
- [Snowflake Marketplace 공식 문서](https://docs.snowflake.com/en/collaboration/collaboration-marketplace-about)
- [VECTOR 데이터 타입 공식 문서](https://docs.snowflake.com/en/sql-reference/data-types-vector)
- [Vector Functions 공식 문서](https://docs.snowflake.com/en/sql-reference/functions-vector)
- [Vector Embeddings 가이드](https://docs.snowflake.com/en/user-guide/snowflake-cortex/vector-embeddings)
- [Getting Started with Cortex Agents](https://www.snowflake.com/en/developers/guides/getting-started-with-cortex-agents/)
- [Multi-Agent RAG with Gen2 Warehouses and Cortex](https://www.snowflake.com/en/developers/guides/multi-agent-rag-gen2-cortex/)
