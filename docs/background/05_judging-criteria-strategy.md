# 심사 기준별 점수 극대화 전략

> Snowflake AI & Data Hackathon 2026 Korea — 테크트랙 5개 심사 기준 분석 및 실행 전략

---

## Executive Summary

테크트랙 심사 기준은 (1) 기술 혁신성, (2) 데이터 활용 능력, (3) 문제 해결 능력, (4) 비즈니스 임팩트, (5) Snowflake 활용도(가산점) 5개 항목이다. 타 해커톤 배점 사례와 심사위원 배경을 종합 분석하여 **각 기준별 구체적 실행 방안**과 **Snowflake 가산점 극대화를 위한 기능 활용 로드맵**을 수립한다. 핵심 전략은 "Snowflake 네이티브 End-to-End 파이프라인 + 다중 데이터셋 크로스 분석 + 작동하는 Streamlit 데모"이다.

---

## 목차

1. [타 해커톤 심사 기준 배점 벤치마크](#1-타-해커톤-심사-기준-배점-벤치마크)
2. [심사 기준 5개별 심층 분석 및 점수 극대화 전략](#2-심사-기준-5개별-심층-분석-및-점수-극대화-전략)
3. [Snowflake 가산점 극대화를 위한 기능 활용 로드맵](#3-snowflake-가산점-극대화를-위한-기능-활용-로드맵)
4. [심사위원 배경 기반 가중치 추정](#4-심사위원-배경-기반-가중치-추정)
5. [종합 실행 매트릭스](#5-종합-실행-매트릭스)
6. [시사점 및 전략적 함의](#6-시사점-및-전략적-함의)

---

## 1. 타 해커톤 심사 기준 배점 벤치마크

### 1.1 국내외 해커톤 배점 사례

| 해커톤 | 기술/혁신 | 데이터/구현 | 문제해결 | 비즈니스 | 기타 | 출처 |
|--------|----------|------------|---------|---------|------|------|
| **HackNY** | 40% (Technical Achievement) | - | - | 30% (Practicality) | 30% (Creativity) | TAIKAI |
| **서울 HW 해커톤** | 소스품질 + 구현완성도 | 플랫폼 활용 | 기획우수성 | - | 참가자 평가 20% | 서울해커톤 |
| **국토교통 빅데이터** | 기술성 | 데이터 활용 | - | 실효성 20% | 창의성 | DACON |
| **Ethical AI Hackathon (CGU)** | Technical Innovation | Working Solution | Imagination | Potential Impact | - | CGU Research |
| **Bellingcat** | Technical Innovation | Working Solution | Imagination of Solution | Positive Impact | - | Bellingcat |
| **Corporate Hackathon** | - | - | - | Business Viability 20% | Feasibility 30%, Impact 25% | Innovation Mode |
| **Snowflake x Accenture** | Technical Execution | Snowflake 활용 | Problem Statement | Business Impact | Presentation | Snowflake |

### 1.2 배점 패턴 분석

**일반적 가중치 분포 (추정)**:
- 기술 관련 항목: 25~40%
- 비즈니스/임팩트: 20~30%
- 창의성/혁신성: 15~30%
- 기타(발표, 완성도 등): 10~20%

**Snowflake 해커톤 특이점**:
- "Snowflake 활용도"가 별도 가산점으로 존재 → 기본 4개 기준 외 추가 점수 획득 가능
- 가산점 구조는 **동점 시 결정적 차별화 요소**로 작용할 가능성이 높음
- Snowflake 주최 해커톤이므로 플랫폼 활용도에 대한 심사위원 관심이 특히 높을 것으로 추정

---

## 2. 심사 기준 5개별 심층 분석 및 점수 극대화 전략

### 2.1 기술 혁신성 — 새로운 기술 활용, 창의적 구현

#### 심사 관점

심사위원은 "이 팀이 기존에 없던 방식으로 문제를 접근했는가?"를 평가한다. 단순히 최신 기술을 나열하는 것이 아니라, 기술 조합의 독창성과 구현의 깊이를 본다.

#### 점수 극대화 실행 방안

| 등급 | 접근 방식 | 예상 점수 영향 |
|------|----------|---------------|
| **하** | 단일 API 호출로 결과 출력 | 기본 점수 |
| **중** | 여러 기술을 조합한 파이프라인 | 평균 이상 |
| **상** | 독자적 아키텍처 + 기술 조합의 시너지 설명 | 상위권 |

**구체적 실행 방안**:

1. **멀티스텝 AI 파이프라인 설계**
   - 데이터 수집 → Snowpark 전처리 → Cortex AI 분석 → Streamlit 시각화
   - 각 단계에서 "왜 이 기술을 선택했는가"에 대한 명확한 근거 준비

2. **하이브리드 AI 아키텍처**
   - Snowflake Cortex AI(내장 LLM) + 외부 모델의 앙상블 또는 파이프라인 결합
   - 예: Cortex AI로 텍스트 감성 분석 → 결과를 피처로 활용 → Snowpark ML 모델 학습

3. **에이전트 기반 접근**
   - Snowflake Intelligence의 에이전트 기능을 활용한 자연어 기반 데이터 질의 시스템
   - 사용자가 자연어로 질문하면 자동으로 SQL 생성 → 분석 → 시각화까지 자동화

4. **기술 차별화 포인트 명시**
   - 발표 시 "기존 접근법 vs 우리 접근법" 비교 슬라이드 포함
   - 기술 선택의 trade-off를 인지하고 있음을 보여주기

### 2.2 데이터 활용 능력 — 제공 데이터 효과적 활용

#### 심사 관점

제공 데이터셋(NextTrade, RICHGO, SPH, 아정당) 4개 중 얼마나 많은 데이터를 의미 있게 활용했는지, 데이터에서 비자명한 인사이트를 도출했는지를 평가한다. 심사위원 4명이 데이터 제공사 관계자인 점이 핵심.

#### 점수 극대화 실행 방안

| 등급 | 접근 방식 | 예상 점수 영향 |
|------|----------|---------------|
| **하** | 1개 데이터셋만 단순 조회 | 감점 요인 |
| **중** | 2개 데이터셋 활용 + 기본 분석 | 평균 |
| **상** | 3~4개 데이터셋 크로스 분석 + Marketplace 데이터 결합 | 상위권 |

**구체적 실행 방안**:

1. **다중 데이터셋 크로스 분석 시나리오**
   - NextTrade(주식) × RICHGO(부동산): 금융 자산 간 상관관계 분석
   - SPH(지역 빅데이터) × RICHGO(부동산): 지역 특성이 부동산 가격에 미치는 영향
   - 아정당(통신) × SPH(지역): 통신 서비스 이용 패턴과 지역 특성 관계
   - 전체 결합: 종합 자산/생활 인사이트 대시보드

2. **데이터 품질 관리 시연**
   - 결측값 처리, 이상치 탐지, 데이터 정규화 과정을 코드로 보여주기
   - Snowpark DataFrame API를 활용한 전처리 파이프라인

3. **피처 엔지니어링**
   - 원본 데이터에서 파생 변수 생성 (이동평균, 변화율, 계절성 지표 등)
   - 데이터셋 간 조인 키 설계 및 시간/공간 기준 매핑 로직

4. **Snowflake Marketplace 데이터 결합**
   - 제공 데이터 외 Marketplace에서 보충 데이터(날씨, 경제 지표 등) 획득
   - "Snowflake 에코시스템 내에서 데이터 확장" 어필

### 2.3 문제 해결 능력 — 명확한 접근 방식, 논리성

#### 심사 관점

문제를 어떻게 정의하고, 어떤 논리적 단계로 해결했는지를 평가한다. "이 팀은 문제를 체계적으로 접근했는가?"가 핵심 질문.

#### 점수 극대화 실행 방안

| 등급 | 접근 방식 | 예상 점수 영향 |
|------|----------|---------------|
| **하** | 문제 정의 불명확, 솔루션 맥락 없음 | 감점 요인 |
| **중** | 문제 정의 + 솔루션 + 결과 | 평균 |
| **상** | 가설 → 검증 → 반복 + 실패 경험 공유 + 정량 메트릭 | 상위권 |

**구체적 실행 방안**:

1. **Problem-Hypothesis-Approach-Result(PHAR) 프레임워크**
   ```
   Problem: [구체적 문제 정의 — 누구의 어떤 pain point인가]
   Hypothesis: [이 문제는 X 데이터를 Y 방법으로 분석하면 해결할 수 있다]
   Approach: [Snowflake 기반 기술 구현 단계]
   Result: [정량적 결과 — 정확도, 처리 속도, 비용 절감 등]
   ```

2. **논리적 흐름의 시각화**
   - 문제 해결 과정을 플로차트/다이어그램으로 1페이지에 정리
   - 각 단계에서의 의사결정 근거 명시

3. **실패 경험 포함**
   - "처음에 A 방법을 시도했으나 B 이유로 실패 → C 방법으로 전환하여 성공"
   - 해커톤 심사에서 실패 경험 공유는 문제 해결 깊이를 보여주는 강력한 시그널

4. **정량적 메트릭 제시**
   - Before/After 비교 수치
   - 모델 성능: 정확도, F1 Score, RMSE 등
   - 처리 성능: 쿼리 응답 시간, 데이터 처리량

### 2.4 비즈니스 임팩트 — 실제 가치 창출 가능성

#### 심사 관점

"이 솔루션이 실제로 돈이 되는가? 누가 쓸 것인가?"를 평가한다. 기술적으로 뛰어나더라도 비즈니스 가치가 불명확하면 최고 점수를 받기 어렵다.

#### 점수 극대화 실행 방안

| 등급 | 접근 방식 | 예상 점수 영향 |
|------|----------|---------------|
| **하** | 비즈니스 모델 미제시 | 감점 요인 |
| **중** | "유용할 것이다" 수준의 일반적 언급 | 평균 |
| **상** | TAM/SAM 제시 + 구체적 수익/비용 시나리오 + 도입 고객 시나리오 | 상위권 |

**구체적 실행 방안**:

1. **시장 규모 간략 제시**
   - TAM(전체 시장) → SAM(접근 가능 시장) → SOM(목표 시장) 3단계
   - 예: "한국 부동산 데이터 분석 시장 X조원 → 개인 투자자 세그먼트 Y억원"

2. **Before/After 시나리오**
   - 현재 상태(As-Is): 수동 분석, 정보 비대칭, 의사결정 지연
   - 도입 후(To-Be): 자동화된 인사이트, 실시간 알림, 의사결정 시간 단축
   - 구체적 수치로 차이 표현 (예: "분석 시간 8시간 → 15분")

3. **고객 페르소나 & 유스케이스**
   - 구체적인 사용자 프로필 1~2개 제시
   - 각 페르소나가 솔루션을 어떻게 사용하는지 시나리오 설명

4. **수익 모델 제시**
   - SaaS 구독 / 데이터 리포트 판매 / B2B API 서비스 등
   - 가격 책정 근거와 예상 매출 시뮬레이션 (보수적/낙관적)

5. **심사위원 기업과 연결**
   - 리치고/SPH/아정당/LG U+가 이 솔루션의 잠재 고객 또는 파트너가 될 수 있음을 암시
   - 해당 기업의 기존 서비스와 시너지 가능성 언급

### 2.5 Snowflake 활용도 — 가산점 항목

#### 심사 관점

Snowpark, Cortex AI, Snowflake Intelligence, Snowflake Marketplace, Streamlit 등 Snowflake 플랫폼 기능을 얼마나 깊이 있게 활용했는지를 평가한다. **가산점**이므로 기본 4개 기준과 별도로 추가 점수를 획득할 수 있는 유일한 항목.

#### 점수 극대화 실행 방안

| 등급 | 접근 방식 | 예상 가산점 |
|------|----------|------------|
| **하** | Snowflake를 단순 데이터 저장소로만 사용 | 가산점 없음 |
| **중** | 1~2개 기능 활용 (예: Snowpark + Streamlit) | 일부 가산점 |
| **상** | 4~5개 기능 통합 활용 + End-to-End 파이프라인 | 최대 가산점 |

**구체적 실행 방안 → 섹션 3에서 상세 로드맵 제시**

---

## 3. Snowflake 가산점 극대화를 위한 기능 활용 로드맵

### 3.1 가산점 대상 기능 총정리

| 기능 | 설명 | 활용 난이도 | 어필 효과 |
|------|------|-----------|----------|
| **Snowpark** | Python/Java/Scala로 Snowflake 내 데이터 처리 및 ML | 중 | 높음 |
| **Cortex AI** | 내장 LLM 함수 (감성 분석, 요약, 번역, 텍스트 생성 등) | 낮음~중 | 높음 |
| **Snowflake Intelligence** | 자연어 기반 데이터 질의 에이전트 | 중~높 | 매우 높음 |
| **Snowflake Marketplace** | 외부 데이터셋 마켓플레이스 | 낮음 | 중 |
| **Streamlit** | 인터랙티브 웹 앱 / 대시보드 | 낮음~중 | 높음 |

### 3.2 기능별 활용 전략

#### A. Snowpark — 데이터 파이프라인의 핵심

**용도**: Snowflake 내부에서 Python으로 데이터 전처리, 피처 엔지니어링, ML 모델 학습/추론

**구현 로드맵**:
```
Step 1: Snowpark Session 설정 및 데이터 로드
Step 2: DataFrame API로 데이터 클렌징/변환
Step 3: Snowpark ML로 모델 학습 (또는 Stored Procedure로 ML 파이프라인)
Step 4: UDF(User Defined Function)로 추론 로직 배포
```

**어필 포인트**: "모든 연산이 Snowflake 내부에서 수행되므로 데이터 이동 없이 보안과 성능을 동시에 확보"

#### B. Cortex AI — AI 기능의 빠른 적용

**용도**: SQL 함수로 LLM 기능 즉시 활용 (별도 모델 배포 불필요)

**핵심 함수와 활용 시나리오**:

| 함수 | 기능 | 활용 시나리오 |
|------|------|-------------|
| `CORTEX.COMPLETE()` | 텍스트 생성/질의응답 | 데이터 기반 자연어 인사이트 생성 |
| `CORTEX.AI_SENTIMENT()` | 감성 분석 (7개 언어) | 뉴스/리뷰 데이터 감성 점수화 |
| `CORTEX.AI_SUMMARIZE()` | 텍스트 요약 | 대량 문서 자동 요약 리포트 |
| `CORTEX.AI_TRANSLATE()` | 다국어 번역 | 해외 데이터 한국어 변환 |
| `CORTEX.AI_EMBED()` | 벡터 임베딩 (텍스트/이미지) | 유사도 검색, RAG 시스템 |
| `CORTEX.AI_CLASSIFY()` | 멀티모달 분류 | 데이터 카테고리 자동 분류 |

**구현 로드맵**:
```
Step 1: AI_SENTIMENT()로 텍스트 데이터 감성 분석 (가장 쉬운 진입점)
Step 2: COMPLETE()로 분석 결과 자연어 해석 생성
Step 3: AI_SUMMARIZE()로 대량 데이터 요약 리포트
Step 4: AI_EMBED()로 벡터 검색 기반 RAG 시스템 (심화)
```

#### C. Snowflake Intelligence — 차세대 데이터 질의

**용도**: 자연어 기반 데이터 질의, 에이전트 오케스트레이션

**핵심 기능**:
- 사용자가 자연어로 질문 → Cortex Agent가 자동으로 워크플로우 계획
- 구조화 데이터: Cortex Analyst가 자연어 → SQL 변환
- 비구조화 데이터: Cortex Search로 관련 텍스트 검색
- 2025년 11월 GA(General Availability) 달성

**구현 로드맵**:
```
Step 1: Semantic Model 정의 (데이터셋의 비즈니스 의미 매핑)
Step 2: Cortex Analyst 설정 (자연어 → SQL 변환)
Step 3: Cortex Search 설정 (비구조화 데이터 검색)
Step 4: Snowflake Intelligence Agent 통합 (End-to-End 자연어 질의)
```

**어필 포인트**: "비기술 사용자도 자연어로 데이터 인사이트를 얻을 수 있는 민주화된 데이터 접근"

#### D. Snowflake Marketplace — 데이터 확장

**용도**: 외부 데이터셋 탐색 및 즉시 활용

**활용 전략**:
- 제공 4개 데이터셋의 분석 가치를 높이는 보충 데이터 확보
- 예: 경제 지표, 날씨 데이터, 인구 통계 등
- "Snowflake Marketplace에서 X 데이터를 추가 획득하여 분석 범위를 확장했다"고 명시

#### E. Streamlit — 최종 결과물 시각화

**용도**: 인터랙티브 웹 앱으로 분석 결과 시각화 및 데모

**구현 로드맵**:
```
Step 1: 기본 대시보드 레이아웃 (차트, 테이블, 필터)
Step 2: Snowflake 데이터 실시간 연동
Step 3: 인터랙티브 요소 추가 (사용자 입력 → 실시간 분석)
Step 4: Cortex AI 함수 연동 (자연어 질의 인터페이스)
Step 5: 디자인 폴리싱 (테마, 레이아웃, 반응형)
```

**어필 포인트**: "Streamlit in Snowflake로 데이터가 Snowflake를 떠나지 않는 보안 앱 구현"

### 3.3 통합 아키텍처 권장안

```
[데이터 소스]                    [Snowflake 플랫폼]                    [프론트엔드]
                                
NextTrade ──┐                  ┌─ Snowpark ─────────┐
RICHGO ─────┤                  │  (전처리/피처엔지니어링) │
SPH ────────┼── 데이터 로드 ──→│  (ML 모델 학습/추론)   │──→ Streamlit App
아정당 ──────┤                  │                     │     (대시보드)
Marketplace ┘                  ├─ Cortex AI ─────────┤     (데모)
                               │  (감성분석/요약/생성)   │
                               ├─ Intelligence ──────┤
                               │  (자연어 질의 에이전트) │
                               └─────────────────────┘
```

### 3.4 학습 우선순위 (시간 제약 고려)

| 우선순위 | 기능 | 학습 시간(추정) | ROI |
|---------|------|---------------|-----|
| 1 | **Streamlit** | 4~8시간 | 최종 데모 품질 직결 |
| 2 | **Snowpark** (DataFrame API) | 8~12시간 | 데이터 파이프라인 핵심 |
| 3 | **Cortex AI** (기본 함수) | 2~4시간 | 가산점 확보 최소 투자 |
| 4 | **Marketplace** | 1~2시간 | 데이터 확장 간편 |
| 5 | **Snowflake Intelligence** | 8~16시간 | 어필 효과 높으나 학습 비용 큼 |

> **권장**: 시간이 부족하면 Streamlit + Snowpark + Cortex AI 기본 함수에 집중. Snowflake Intelligence는 시간 여유가 있을 때 도전.

---

## 4. 심사위원 배경 기반 가중치 추정

### 4.1 심사위원별 전문 분야와 관심 기준

| 심사위원 | 전문 분야 | 높은 가중치 기준 (추정) | 낮은 가중치 기준 (추정) |
|---------|----------|---------------------|---------------------|
| **최기영** (Snowflake Korea) | 클라우드 비즈니스, GTM | Snowflake 활용도, 비즈니스 임팩트 | 기술 세부 구현 |
| **김재구** (리치고) | 부동산 데이터, AI 예측 | 데이터 활용 능력, 기술 혁신성 | 프레젠테이션 |
| **김선경** (SPH) | GIS, 공간 빅데이터 | 데이터 활용 능력, 문제 해결 | 비즈니스 모델 |
| **이하석** (아정당) | 그로스 마케팅, 데이터 드리븐 | 비즈니스 임팩트, 데이터 활용 | 기술 구현 깊이 |
| **전병기** (LG U+) | AI/LLM, 박사급 기술 | 기술 혁신성, Snowflake 활용도 | 비즈니스 모델 |
| **김대식** (네이버 웹툰) | AI 조직 운영, 추천 시스템 | 기술 혁신성, 문제 해결 능력 | - |

### 4.2 종합 가중치 추정

심사위원 6명의 전문 분야를 종합하면 각 기준의 실질 가중치는 다음과 같이 추정된다:

| 심사 기준 | 추정 실질 가중치 | 근거 |
|----------|----------------|------|
| **기술 혁신성** | 25~30% | 전병기(박사), 김대식(AI 총괄), 김재구(AI 예측) — 기술 전문가 3명 |
| **데이터 활용 능력** | 25~30% | 데이터 제공사 관계자 4명(김재구, 김선경, 이하석, 전병기) |
| **문제 해결 능력** | 15~20% | 전반적으로 고른 관심, 특히 김선경(컨설팅), 김대식(스타트업) |
| **비즈니스 임팩트** | 15~20% | 최기영(엔터프라이즈), 이하석(마케팅) — 비즈니스 관점 2명 |
| **Snowflake 활용도 (가산점)** | +5~15% | 최기영(Snowflake 지사장) — 주최사 대표의 핵심 관심사 |

### 4.3 가중치 기반 전략적 자원 배분

```
기술 혁신성 (25-30%) ████████████████████████████░░  → 개발 시간의 30% 투자
데이터 활용 (25-30%) ████████████████████████████░░  → 개발 시간의 30% 투자
문제 해결   (15-20%) ████████████████░░░░░░░░░░░░░░  → 발표 구성에 반영
비즈니스    (15-20%) ████████████████░░░░░░░░░░░░░░  → 발표 1~2분 할애
SF 활용도   (+5-15%) ████████████░░░░░░░░░░░░░░░░░░  → 전체 아키텍처에 녹이기
```

---

## 5. 종합 실행 매트릭스

### 5.1 기준별 핵심 실행 항목 체크리스트

| # | 실행 항목 | 관련 기준 | 우선순위 | 난이도 |
|---|----------|----------|---------|-------|
| 1 | 다중 데이터셋(3개+) 크로스 분석 구현 | 데이터 활용 | 최상 | 중 |
| 2 | Snowpark 기반 데이터 파이프라인 구축 | 기술 혁신 + SF 활용 | 최상 | 중 |
| 3 | Streamlit 인터랙티브 데모 앱 개발 | SF 활용 + 문제 해결 | 최상 | 중 |
| 4 | Cortex AI 함수 2개+ 활용 | SF 활용 + 기술 혁신 | 상 | 낮 |
| 5 | PHAR 프레임워크 기반 발표 구성 | 문제 해결 | 상 | 낮 |
| 6 | Before/After + TAM/SAM 비즈니스 슬라이드 | 비즈니스 임팩트 | 상 | 낮 |
| 7 | Marketplace 데이터 1개+ 추가 활용 | 데이터 활용 + SF 활용 | 중 | 낮 |
| 8 | Snowflake Intelligence 자연어 질의 구현 | SF 활용 + 기술 혁신 | 중 | 높 |
| 9 | 정량적 성능 메트릭 제시 | 문제 해결 | 중 | 중 |
| 10 | 심사위원별 Q&A 예상 답변 준비 | 전체 | 중 | 낮 |

### 5.2 시간 제약별 전략 (Tier 구분)

**Tier 1 — 최소 필수 (20시간 이내)**:
- 항목 #1, #2, #3, #5, #6 집중
- Snowpark + Streamlit + 다중 데이터셋 기본 분석

**Tier 2 — 경쟁력 확보 (40시간 이내)**:
- Tier 1 + 항목 #4, #7, #9
- Cortex AI 함수 추가, Marketplace 데이터 보강, 성능 메트릭

**Tier 3 — 수상 극대화 (60시간 이상)**:
- Tier 2 + 항목 #8, #10
- Snowflake Intelligence 구현, 심사위원별 Q&A 완벽 대비

---

## 6. 시사점 및 전략적 함의

### 6.1 핵심 인사이트

1. **데이터 활용 = 최우선**: 심사위원 6명 중 4명이 데이터 제공사 관계자. 자사 데이터를 성의 있게 활용하지 않는 팀은 사실상 탈락 리스크.

2. **Snowflake 가산점 = 게임 체인저**: 기본 4개 기준에서 팀 간 점수 차이가 크지 않을 경우, 가산점이 순위를 결정. 최기영 지사장(Snowflake Korea)이 심사위원이므로 플랫폼 활용의 진정성이 중요.

3. **기술 깊이 vs 비즈니스 폭**: 전병기(박사)와 김대식(AI 총괄)은 기술 깊이를 보고, 최기영과 이하석은 비즈니스 임팩트를 본다. 둘 다 만족시키는 균형이 필요.

4. **가산점 함정 주의**: Snowflake 기능을 "써봤다"만으로는 가산점 확보 어려움. 핵심 파이프라인에 자연스럽게 통합되어야 진정한 활용으로 인정받음.

### 6.2 최종 전략 요약

```
[필수] 다중 데이터셋 크로스 분석 + Snowpark 파이프라인 + Streamlit 데모
[강력 권장] Cortex AI 함수 활용 + Marketplace 데이터 결합
[차별화] Snowflake Intelligence 자연어 질의 + 에이전트 시스템
[발표] PHAR 프레임워크 + Before/After + 정량 메트릭 + 심사위원 맞춤 Q&A
```

---

## 출처

1. [Snowflake x Streamlit 해커톤 2026 Korea 공식 페이지](https://www.snowflake.com/snowflake-hackathon-2026-korea/)
2. [Hackathon judging: 6 criteria to pick winning projects - TAIKAI](https://taikai.network/en/blog/hackathon-judging)
3. [How to judge a hackathon: 5 criteria to pick winners - Eventornado](https://eventornado.com/blog/how-to-judge-a-hackathon-5-criteria-to-pick-winners)
4. [4 Criteria to Apply When Judging a Hackathon - hackathon.com](https://tips.hackathon.com/article/4-criteria-to-apply-when-judging-a-hackathon)
5. [Crafting Effective Hackathon Judging Criteria - EventFlare](https://eventflare.io/journal/crafting-effective-hackathon-judging-criteria-a-step-by-step-guide)
6. [How to win a hackathon: Advice from 5 seasoned judges - Devpost](https://info.devpost.com/blog/hackathon-judging-tips)
7. [How to Judge a Hackathon: 4 Criteria - Relativity](https://www.relativity.com/blog/how-to-judge-a-hackathon-4-criteria-to-picking-a-winner/)
8. [JUDGING RUBRIC - Ethical AI Hackathon (CGU)](https://research.cgu.edu/hackathon/home/judging-rubric/)
9. [서울 하드웨어 해커톤 심사기준](https://www.seoulhackathon.org/95?category=1238635)
10. [국토교통 빅데이터 온라인 해커톤 - DACON](https://dacon.io/en/competitions/official/235622/overview/rules)
11. [Snowflake Cortex AI Functions - Snowflake Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)
12. [Snowflake Cortex LLM functions: A complete overview (2026) - Flexera](https://www.flexera.com/blog/finops/snowflake-cortex/)
13. [Snowflake Intelligence - 공식 제품 페이지](https://www.snowflake.com/en/product/snowflake-intelligence/)
14. [Snowflake Intelligence (General availability) 2025-11-04 - Snowflake Docs](https://docs.snowflake.com/en/en/release-notes/2025/other/2025-11-04-snowflake-intelligence)
15. [Cortex Analyst - Snowflake Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
16. [Build AI Apps with Streamlit and Snowflake Cortex - Snowflake Guide](https://www.snowflake.com/en/developers/guides/build-ai-apps-with-streamlit-and-snowflake-cortex/)
17. [Build a Multi-Tool AI Agent App with Streamlit and Snowflake Cortex](https://www.snowflake.com/en/developers/guides/build-multi-tool-ai-agent-app-with-streamlit-and-snowflake-cortex/)
18. [RAG 'n' ROLL Hackathon (Snowflake x Mistral) - Devpost](https://snowflake-mistral-rag.devpost.com/)
19. [Snowflake x Accenture Hackathon - 공식 페이지](https://www.snowflake.com/snowflake-x-accenture-hackathon/)
20. [How to Win a Hackathon: Tips, Strategy & Winning Examples - PlacementPreparation](https://www.placementpreparation.io/blog/how-to-win-a-hackathon/)
21. [LGU+, 전병기 AI·데이터그룹장 전무 승진 - 서울경제](https://www.sedaily.com/NewsView/29XCZNUCQL)
22. [김대식 네이버웹툰 이사 AI 기술에 진심 - 아주경제](https://www.ajunews.com/view/20241216094925079)
23. [부동산 시장에 '예측 가능성'을...김재구 데이터노우즈 사장 - 벤처스퀘어](https://www.venturesquare.net/1032213)
