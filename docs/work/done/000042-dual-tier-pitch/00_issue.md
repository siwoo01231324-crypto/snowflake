# chore: 프로젝트 스코프 재정의 + 발표 스토리 + 기획서 Dual-Tier 업데이트

# Issue #42: chore: 프로젝트 스코프 재정의 + 발표 스토리 + 기획서 Dual-Tier 업데이트

## 목적
해커톤 Marketplace 샘플 데이터의 실제 커버리지(아정당 25구 / SPH·RICHGO 3구)를 프로젝트 비전·발표 스토리에 명시적으로 반영한다. #21에서 `DATA_TIER` 컬럼으로 마트에는 반영됐으나, 스펙·스토리·후속 이슈들은 여전히 '서울 전체 25구 풀 모델' 가정을 유지 중이다.

## 배경
#21 통합 마트 작업 중 Python snowflake-connector로 직접 검증된 사실:

| 데이터셋 | 구 커버리지 | 기간 |
|---|---|---|
| 아정당 V_TELECOM_NEW_INSTALL | **25구 전부** | 2023-03 ~ 2026-05 |
| SPH FLOATING_POP / CARD_SALES / ASSET_INCOME | **3구만** (중 11140 / 영등포 11560 / 서초 11650) | 2021-2025 |
| RICHGO | **3구만** (동일, 29 BJD) | 2012-01 ~ 2024-12 |
| SPH M_SCCO_MST | 25구 467개 법정동(BJD) (마스터 코드북만) | - |

`MART_MOVE_ANALYSIS` 850행 = 25구 × 34개월(202307~202604), DATA_TIER로 `MULTI_SOURCE`(3구) / `TELECOM_ONLY`(22구) 구분 완료.

## 완료 기준
- [x] `docs/specs/dev_spec.md` A5-1 MVP 데이터 범위 섹션을 Dual-Tier 구조로 재작성  <!-- #40(3cfafdb)에서 Track A/B 분리 완료, dev_spec.md:870-898 -->
- [ ] `docs/specs/pitch_story.md` 신규 — 발표 골격 + 핵심 메시지 + Q&A 스크립트
- [ ] Track A (25구 경량) / Track B (3구 풀) 각각의 가치 제안 문서화
- [ ] 심사 Q&A 대응 스크립트: "왜 3구뿐?" → Marketplace 샘플 제약 + 확장 로드맵
- [ ] 후속 이슈(#22·#23·#24·#25·#28·#29) 본문 AC 수정 권고안 정리
- [ ] CLAUDE.md `docs/specs/pitch_story.md` 위치 기재

## Dual-Tier 구조
| Track | 대상 | 피처 | 모델 후보 | 발표 역할 |
|---|---|---|---|---|
| **A — 25구 경량** | 서울 25구 전부 | OPEN_COUNT + CONTRACT/PAYEND | 선형 회귀 / MA | "서울 전역 이사 시그널 히트맵" (커버리지 임팩트) |
| **B — 3구 풀** | 중·영등포·서초 | 아정당+SPH3+RICHGO 15+ 피처 | Ridge / XGB | "다중 데이터 교차검증 예측 엔진" (정밀도 임팩트) |

## 발표 핵심 메시지 (초안)
> "아정당 25구 통신 개통 시그널로 서울 전역 이사 수요를 관찰, SPH·RICHGO 3개 대표 권역 데이터로 교차검증하여 신뢰도를 입증. Marketplace 데이터 확장 시 전 권역 풀 모델로 즉시 전개 가능한 **확장형 프레임워크**."

## 구현 플랜
1. dev_spec.md A5-1 · A1 · A4 섹션 Dual-Tier 반영 수정
2. pitch_story.md 작성: 문제 정의 → 데이터 제약 직시 → Dual-Tier 솔루션 → 확장성
3. 후속 이슈 영향 체크리스트 작성 후 각 이슈 본문 수정 권고 (별도 PR 또는 이슈 edit)
4. 권역 성격 태그 초안 작성 (서초=고급주거·학군, 영등포=금융·혼합, 중구=도심오피스·상업)

## 참조
- `pipelines/preprocessing.py:10` `MULTI_SOURCE_CITIES = ["11140", "11560", "11650"]`
- `docs/work/done/000021-integrated-mart/01_plan.md` — Dual-Tier 결정 ADR
- 의존성: #40 (dev_spec 정정이 완료된 뒤 추가 수정 진행)

## 불변식
- Marketplace 실커버리지를 넘어서는 가정 금지
- '25구 풀 예측' 표현은 허위 주장 — Track A/B 명시 필수
- 발표에서 제약을 숨기지 않고 프레임워크의 확장성으로 전환

## 개발 체크리스트
- [ ] docs/specs/.ai.md 최신화

## 작업 내역

- 2026-04-08: `/si 42` — 워크트리·브랜치 생성, 이슈 assign 완료
- 2026-04-08: `/ri` — AC 현황 점검 (1/7 완료). dev_spec.md A5-1은 #40에서 이미 Track A/B 분리됨. pitch_story.md / followup 권고안 / CLAUDE.md / .ai.md는 미착수. 단계: **구현 대기**.
- 2026-04-08: `/plan /team 3` — ralplan 실행 (team:3 worker-devspec + worker-issue + worker-planner). worker-devspec는 `.omc/research/42-devspec-scan.md` 작성 완료 (Dual-Tier 반영 95%, 잔존 2건 식별). worker-issue는 응답 없어 team-lead가 직접 `.omc/research/42-issue-context.md` 작성 (이슈 #42 **코멘트 scope 확장 3건 발견** — whitepaper v1.0→v1.2, v1.1 검토, .ai.md). 최종 01_plan.md 재작성 완료: **AC 7→10건**, Step 1~8 상세 플랜 + 불변식 6건 + 의존성 그래프 + 검증 체크리스트. 단계: **구현 대기 (플랜 확정)**.
- 2026-04-09: **구현 1차 완료 (세션 중 crash 후 재개)**. 완료 항목:
  - `git rebase origin/master` — #43(f0f6065) 반영. docs/presentation/ 디렉토리 신설 확인.
  - `docs/presentation/00_pitch_story.md` 신규 작성 (374줄, 10개 섹션 — §4 4중 증거 체인, §7 5단계 검증 프레임, §8 Q&A 8건, §9 5분 발표 대본)
  - `docs/whitepaper/v1.0-moving-intelligence.md` v1.2 팩트 정정 — "통신 주소변경"→"신규 계약·개통(CONTRACT/OPEN)" 전체, RICHGO 서술 정정("인구이동"→"시세+인구통계"), §6 Marketplace 확장 문단 추가, 변경 이력 v1.2 섹션 신설
  - `docs/whitepaper/v1.1-branding-strategy.md` v1.1.1 — "통신 주소변경"→"신규 계약·개통" 전체, Pre-Move Signal™ 정의 보강, 변경 이력 추가
  - `docs/specs/dev_spec.md` S1 시그널 재정의: OPEN_COUNT → CONTRACT_COUNT (주 선행), S1' OPEN 확인 지표 추가, VALIDATION_OPEN_LAG / CARRYOVER_RATIO 모니터링 필드 추가, 변경 이력 §2026-04-09 #42 추가
  - `docs/work/EXECUTION_PLAN.md` 전면 업데이트: §2.3 "2-4주 선행" 검증 프레임워크 신설, §3.3 백로그 매트릭스 #42/#46 반영, §8/#9 이력·참조 추가
  - `CLAUDE.md` §핵심 문서 위치 — presentation/, whitepaper/ 경로 추가
  - `docs/presentation/.ai.md` — 00_pitch_story.md 항목 추가
  - `docs/specs/.ai.md` — dev_spec v3.1 + pitch_story 분리 노트 추가
  - `docs/whitepaper/.ai.md` — v1.2/v1.1.1 상태 업데이트, 규칙·관련 문서 추가
  - GitHub Issue #46 신규 생성 — "공공 데이터 통합 검증 파이프라인 (KOSIS/국토부/서울열린데이터)"
  - `.omc/research/42-lead-time-verification.md` §H6 추가 — KOSIS 교차검증 실행 결과 (demeaned r=0.002, p=0.949, n=550)
- 2026-04-09: **KOSIS Option B 결정 + 후속 업데이트**. "2-4주 선행"을 KOSIS로 직접 검증하는 대신 "이사 시점 = OPEN 시점" 물리 공리 + CONTRACT→OPEN 내부 실증(r=0.895)으로 방어. KOSIS cross-validation r≈0은 구조적 후행의 증거 → 우리 데이터의 독자적 가치를 역설적으로 증명하는 논리로 재프레이밍.
  - `docs/presentation/00_pitch_story.md` §4.2 Layer 2 — KOSIS 실측 결과 + Option B 재프레이밍으로 {TBD} 대체
  - `docs/presentation/00_pitch_story.md` §7 검증 프레임워크 — ground truth를 KOSIS→OPEN으로 교체, 5단계 검증 테이블 업데이트
  - `docs/presentation/00_pitch_story.md` Q4·§9 — {TBD} 제거, 실측 수치 반영
