# Snowflake 해커톤/공모전 수상작 사례 분석

## Executive Summary

Snowflake는 2024년부터 글로벌 및 한국에서 다수의 해커톤과 공모전을 개최해왔다. 본 문서는 과거 Snowflake 주관/후원 해커톤 수상작들을 체계적으로 분석하여, 2026 Snowflake AI & Data Hackathon Korea 참가 전략 수립의 기초 자료로 활용한다. 수상작들은 공통적으로 **실제 비즈니스 문제 해결**, **Snowflake 플랫폼 기능의 깊이 있는 활용**, **직관적인 Streamlit 기반 UI**를 특징으로 한다.

---

## 목차

1. [Snowflake x Streamlit 해커톤 Korea 2025 (1회)](#1-snowflake-x-streamlit-해커톤-korea-2025-1회)
2. [Arctic + Streamlit 해커톤 (The Future of AI is Open, 2024)](#2-arctic--streamlit-해커톤-the-future-of-ai-is-open-2024)
3. [RAG 'n' ROLL 해커톤 (Snowflake x Mistral, 2024-2025)](#3-rag-n-roll-해커톤-snowflake-x-mistral-2024-2025)
4. [Snowflake x Accenture 해커톤 (인도, 2025-2026)](#4-snowflake-x-accenture-해커톤-인도-2025-2026)
5. [Snowflake Startup Challenge 2025](#5-snowflake-startup-challenge-2025)
6. [수상작 공통 기술 패턴 분석](#6-수상작-공통-기술-패턴-분석)
7. [2026 Korea 해커톤 시사점](#7-2026-korea-해커톤-시사점)

---

## 1. Snowflake x Streamlit 해커톤 Korea 2025 (1회)

> **가장 직접적인 선례** — 동일 주최(Snowflake Korea), 유사 평가기준, 일부 동일 데이터셋(SPH)

### 개요
- **일시**: 2025년 3월 26일 접수 ~ 5월 14일 결선 (서울 C-Square)
- **참가 규모**: 약 360명 (개인 참가만 허용, 팀 불가)
- **데이터셋**: DataKnows(아파트 시세·인구), Loplat(유동인구·날씨), SPH(유동인구·소비·자산)
- **평가기준**: 기능완성도(25%), Snowflake 활용도(25%), 코드 품질(15%), Streamlit 앱/예측기능(15%), 에러 처리(10%), 창의성(10%)
- **상금**: 1위 MacBook Air M4, 2위 PS5 Slim, 3위 Apple Watch SE

### 수상작 분석

| 순위 | 수상자 | 소속 | 프로젝트명 | 핵심 내용 |
|------|--------|------|-----------|-----------|
| **1위** | 박준호 | 네이버 (데이터 엔지니어) | 주가 분석 대시보드 | 백화점 방문 데이터 + 카드 소비 내역을 결합하여 개인투자자용 투자 전략 플랫폼 구축 |
| **2위** | 최민영 | 비트센싱 (센서 데이터 엔지니어) | 서울 상권 분석 전략 시뮬레이션 | 지역별 카드 소비 내역 기반 상권 분석 도구의 진입장벽 해소 |
| **3위** | 성지욱 | SK C&C (데이터 엔지니어) | NexGen Index | 인구·자산·소득 등 지역별 데이터 기반 가족 친화 상권 분석 |
| **4위** | 심동현 | HNIX (산업개발IS팀장) | 아파트 시세 예측 모델 | 아파트 시세 + 자산소득 + 유동인구 데이터로 ML 예측 모델 구현 |

### 핵심 인사이트
- **수상자 전원 현직 데이터 엔지니어** — 실무 경험에서 나온 도메인 이해도가 차별화 요소
- **금융/부동산/상권** 주제에 집중 — 제공된 데이터셋(소비·유동인구·시세)과 직결되는 실용적 주제 선택
- **Snowflake Marketplace 데이터 적극 활용** — 외부 데이터가 아닌 제공 데이터를 깊이 있게 분석
- **1위 심사평**: "양질의 정보 접근성이 낮은 개인투자자에게 객관적 데이터 지표를 제공" — **사회적 가치(정보 격차 해소)** 강조

---

## 2. Arctic + Streamlit 해커톤 (The Future of AI is Open, 2024)

### 개요
- **일시**: 2024년 4월 30일 ~ 5월 21일 (온라인, Devpost)
- **주제**: Snowflake Arctic(오픈소스 LLM) + Streamlit로 AI 앱 개발
- **상금**: 1위 $5,000, 2위 $2,000, 3위 $1,000
- **수상작 수**: 10개 (3개 본상 + 7개 Honorable Mention)

### 수상작 분석

| 순위 | 프로젝트명 | 개발자 | 핵심 기능 | 차별점 |
|------|-----------|--------|----------|--------|
| **1위** | WizSearch | Sanjay Kumar | AI 검색 어시스턴트 — 질문에 대해 인터넷 정보를 검색·합성하여 출처 포함 답변 생성 | Arctic 모델의 정보 합성 능력을 최대한 활용, 검색+요약+출처 제공의 완결된 UX |
| **2위** | AdImpact Databot | Michael Schader 외 3명 | 자연어→SQL 변환 기반 데이터 조회 도구 (2024 미국 정치 광고·지출 데이터) | LLM 생성 SQL을 파싱·검증하여 보안 확보, 실제 도메인 데이터 활용 |
| **3위** | AskBI | Riya Ponraj 외 3명 | BI 리포트/대시보드에 대한 자연어 질의 도구 | GenAI + 메타데이터 결합으로 기존 BI 리소스 활용도 극대화 |

### Honorable Mention 주요 프로젝트

| 프로젝트명 | 핵심 기능 | 주목할 패턴 |
|-----------|----------|------------|
| Crystal Costs | Snowflake 크레딧 비용 모니터링 및 최적화 AI 에이전트 | **Snowflake 자체를 대상으로 한 메타 솔루션** |
| Arctic Video Citations | 비디오 콘텐츠에 대한 인용 기반 생성 | 멀티모달 응용 |
| The Bad Programmer | 버그가 있는 코드 챌린지 생성으로 디버깅 스킬 향상 | 게이미피케이션 |
| Snow Instructor | 게이미피케이션 기반 Snowflake 학습 도구 | **Snowflake 교육 자체를 주제로** |
| FinnoSQLbot | 금융 데이터 탐색 + SQL 실행 어시스턴트 | Text-to-SQL 패턴 반복 |
| Invisible Insights | SEC 공시 기반 지식그래프로 투자 리스크/기회 분석 | 지식그래프 활용 |

### 핵심 인사이트
- **Text-to-SQL / 자연어 데이터 조회** 패턴이 상위 3개 수상작 중 2개를 차지
- **1위 WizSearch**: 기술적 복잡도보다 **완결된 사용자 경험**(질문→검색→합성→출처)이 핵심 차별화
- **4인 팀이 2위, 3위** 차지 — 개인보다 팀 기반 프로젝트가 기능 완성도에서 유리

---

## 3. RAG 'n' ROLL 해커톤 (Snowflake x Mistral, 2024-2025)

### 개요
- **일시**: 2024년 11월 12일 ~ 2025년 1월 21일 (온라인, Devpost)
- **주제**: Cortex Search(검색) + Mistral LLM(생성) + Streamlit(프론트엔드)로 RAG 앱 개발
- **상금**: 1위 $5,000, 2위 $2,500, 3위 $1,500, 4위 $1,000
- **필수 기술 스택**: Snowflake Cortex Search, Mistral-large2 on Snowflake Cortex, Streamlit Community Cloud

### 수상작 분석

| 순위 | 프로젝트명 | 개발자 | 핵심 기능 | 차별점 |
|------|-----------|--------|----------|--------|
| **1위** | SnowTrail | Jeffry Stevany Chandra | 강의 영상의 핵심 순간 네비게이션 도구 | 교육 분야 실용 문제 해결, 멀티미디어(강의 영상) + RAG 결합 |
| **2위** | ChefMate | Moustafa Ismail 외 2명 | 냉장고 재료 기반 지속가능한 요리 가이드 | "냉장고→요리"라는 직관적 사용 시나리오, 지속가능성 메시지 |
| **3위** | Clarity | Sree Rengavasan R 외 1명 | 고객 지원 티켓을 분석하여 태깅·감정분석·솔루션 식별 | SaaS B2B 실무 문제 해결, 명확한 비즈니스 임팩트 |

### 핵심 인사이트
- **1위 SnowTrail**: 강의 영상이라는 **비정형 데이터**(멀티미디어)에 RAG를 적용 — 텍스트 RAG를 넘어선 창의적 확장
- **필수 스택 준수**: 모든 수상작이 Cortex Search + Mistral + Streamlit 조합을 충실히 활용
- **2위 ChefMate**: 기술적 깊이보다 **일상적 문제 + 사회적 가치(지속가능성)**로 차별화
- **3위 Clarity**: B2B SaaS 도메인의 **명확한 ROI 스토리텔링** — "지원 티켓 처리 시간 단축"이라는 측정 가능한 가치

---

## 4. Snowflake x Accenture 해커톤 (인도, 2025-2026)

### 개요
- **일시**: 2025년 11월 24일 접수 ~ 2026년 1월 20일 수상자 발표
- **대상**: 인도 거주 18세 이상
- **형식**: 2라운드 심사 — 1차 코드/문서 심사(Top 10 선발) → 2차 발표 심사(방갈로르 대면)
- **심사**: Accenture + Snowflake 공동 4인 심사위원
- **평가기준**: 혁신성(30%), 기술 우수성(25%), 비즈니스 가치(25%), UX(20%)

### 문제 유형 (3가지 트랙)

| 트랙 | 주제 | 핵심 요구사항 |
|------|------|-------------|
| Automotive Intelligence | 차량 품질 분석 + 30일 고장 예측 | 텔레메트리·제조·공급망 데이터 통합 |
| Telecom Intelligence | 셀타워 성능 최적화 + 고객 감정 분석 | AI 기반 네트워크 이상 예측 |
| Retail Intelligence | 교차 리테일러 상품 매칭 + 동적 가격 전략 | 엔터티 해상도 파이프라인 |

### 기술 요구사항
- **필수**: SQL, Python, Snowflake, Streamlit
- **가산점**: Cortex, Snowflake ML, REST API 활용

### 핵심 인사이트
- **산업 특화 문제 정의**: 추상적 주제가 아닌 구체적 산업 문제(자동차·통신·유통) 제시
- **혁신성(30%)이 최고 배점** — 기존 방법과의 차별화가 가장 중요한 평가 요소
- **제출물**: 코드 + 5분 데모 영상 + 아키텍처 PPT + GitHub 링크 — 다층적 평가
- **비즈니스 가치(25%)**: ROI와 실용성이 기술력과 동등한 비중

---

## 5. Snowflake Startup Challenge 2025

> **해커톤은 아니지만**, Snowflake 플랫폼 활용의 최고 수준 사례로 참고 가치가 높음

### 수상작: Lumilinks — FleetSense AI
- **분야**: 차량 관리 / IoT / 예측 유지보수
- **솔루션**: 텔레메트릭스 데이터 + 수리 이력 데이터를 활용한 차량 부품 고장 예측 AI
- **기술 스택**: Snowflake Cortex, Document AI, Secure Data Sharing, Snowpark Container Services, UDFs, Native App Framework
- **Streamlit 활용**: Smart Insights(C-level 대시보드), Smart Repair(엔지니어용 수리 예약 도구)
- **비즈니스 임팩트**: 차량 오프로드 시간 최대 30% 감소 (7자리 이상 비용 절감 효과)
- **경쟁**: 100개국 이상 1,000개 이상 스타트업 중 선발

### 핵심 인사이트
- **Snowflake 네이티브 기능의 깊이 있는 활용**: Cortex + Document AI + Container Services + Native App Framework를 모두 활용
- **명확한 정량적 비즈니스 임팩트**: "30% 감소", "7자리 비용 절감" 등 구체적 수치 제시
- **6개월 만에 2개 AI 앱 개발**: 빠른 프로토타이핑 → 프로덕션 전환 스토리

---

## 6. 수상작 공통 기술 패턴 분석

### 6.1 기술 스택 패턴

| 구성 요소 | 빈출 기술 | 비고 |
|----------|----------|------|
| **프론트엔드** | Streamlit (거의 100%) | Snowflake 해커톤의 사실상 필수 기술 |
| **LLM/AI** | Snowflake Cortex, Arctic, Mistral | 해커톤별 지정 모델 우선, Cortex가 최신 트렌드 |
| **데이터 검색** | Cortex Search (RAG) | 비정형 데이터 검색 + LLM 생성의 표준 패턴 |
| **데이터 처리** | SQL + Python (Snowpark) | SQL이 기본, Python은 ML/분석용 보조 |
| **데이터 소스** | Snowflake Marketplace, 제공 데이터셋 | 외부 데이터보다 제공 데이터의 깊이 있는 활용이 유리 |
| **고급 기능** | Document AI, Container Services, Native App | Startup Challenge 수준의 차별화 요소 |

### 6.2 주제/도메인 패턴

| 도메인 | 사례 | 빈도 |
|--------|------|------|
| **금융/투자** | 주가 분석 대시보드, FinnoSQLbot, Invisible Insights | 매우 높음 |
| **부동산/상권** | 상권 분석, NexGen Index, 아파트 시세 예측 | 높음 (특히 한국) |
| **고객 지원/CRM** | Clarity, ChefMate | 보통 |
| **교육/학습** | SnowTrail, Snow Instructor, The Bad Programmer | 보통 |
| **Text-to-SQL / 데이터 조회** | AdImpact Databot, AskBI, FinnoSQLbot | 매우 높음 |
| **산업 IoT/예측** | FleetSense AI, Automotive Intelligence | 보통 |

### 6.3 수상작 공통 성공 요인

1. **실용적 문제 정의**: 추상적 기술 데모가 아닌, 특정 사용자(개인투자자, SaaS 팀, 학생 등)의 구체적 페인포인트 해결
2. **플랫폼 기능 깊이 활용**: 단순 API 호출이 아닌, Cortex Search + LLM + Streamlit의 유기적 결합
3. **완결된 사용자 경험**: 입력→처리→출력→시각화의 전 과정이 데모 가능한 수준으로 구현
4. **비즈니스 임팩트 스토리텔링**: "정보 격차 해소", "처리 시간 단축", "비용 절감" 등 측정 가능한 가치 제시
5. **제공 데이터셋 적극 활용**: 특히 한국 해커톤에서 Marketplace/제공 데이터를 깊이 있게 분석한 팀이 수상

---

## 7. 2026 Korea 해커톤 시사점

### 2025→2026 변화 포인트
- **팀 참가 허용** (2025년은 개인만 가능) — 역할 분담과 기능 완성도 향상 기회
- **테크트랙 + 비즈니스트랙** 분리 — 테크트랙은 코드+데모영상(10분), 발표10분+Q&A3분
- **평가기준 변화**: 기술혁신성, 데이터활용능력, 문제해결능력, 비즈니스임팩트, Snowflake 활용도(가산점)
- **데이터셋 확대**: NextTrade(주식), RICHGO(부동산), SPH(지역빅데이터), 아정당(통신)

### 과거 수상 패턴 기반 전략 제안

1. **데이터셋 교차 활용**: 2025년 수상작은 단일 데이터셋 활용이 주류 → 2026년에는 여러 데이터셋(주식+부동산+통신 등)을 결합한 복합 분석이 차별화 포인트
2. **Cortex 기반 RAG/에이전트 아키텍처**: 2024-2025 글로벌 해커톤 트렌드에 맞춰 Cortex Search + LLM 기반 RAG 또는 AI 에이전트 구현
3. **실용적 금융/부동산 도메인**: 한국 해커톤에서 금융·부동산 주제가 반복적으로 수상 — 제공 데이터셋(NextTrade, RICHGO)과 직결
4. **10분 데모 영상 품질**: 글로벌 해커톤에서 데모 품질이 당락을 좌우 — 스크립트 작성, 리허설 필수
5. **정량적 비즈니스 임팩트 제시**: "X% 시간 절감", "Y명의 사용자에게 Z 가치 제공" 등 구체적 수치

---

## 출처

1. Snowflake Korea, "Snowflake x Streamlit 해커톤 Korea 2025 아카이브", https://www.snowflake.com/snowflake-streamlit-hackathon-korea-archive-2025/
2. StartupN, "스노우플레이크, '스노우플레이크 X 스트림릿 해커톤' 성료", https://www.startupn.kr/news/articleView.html?idxno=52038
3. Devpost, "THE FUTURE OF AI IS OPEN (Arctic + Streamlit Hackathon)", https://arctic-streamlit-hackathon.devpost.com/
4. Streamlit Community, "Arctic + Streamlit hackathon winners!", https://discuss.streamlit.io/t/arctic-streamlit-hackathon-winners/71720
5. Devpost, "RAG 'n' ROLL Amp up Search with Snowflake & Mistral", https://snowflake-mistral-rag.devpost.com/
6. Snowflake, "Snowflake x Accenture Hackathon", https://www.snowflake.com/snowflake-x-accenture-hackathon/
7. Snowflake Blog, "Announcing 2025 Snowflake Startup Challenge Winner: Lumilinks", https://www.snowflake.com/en/blog/startup-challenge-2025-winner/
8. Snowflake Korea, "Snowflake 해커톤 2026 Korea", https://www.snowflake.com/snowflake-hackathon-2026-korea/
9. Seoul Economic Daily, "Snowflake Korea Hosts Second Annual Hackathon Open to Non-Developers", https://en.sedaily.com/technology/2026/03/24/snowflake-korea-hosts-second-annual-hackathon-open-to-non
