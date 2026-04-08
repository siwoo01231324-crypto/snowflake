# Issue #42 구현 플랜 — 현재 상태 (2026-04-09 갱신)

> 초안: 2026-04-08 / 최종 갱신: 2026-04-09 (세션 재개 후 Option B 완료 반영)
>
> **이 파일의 목적**: 완료/미완료 상태 추적. 상세 설계는 `docs/work/EXECUTION_PLAN.md` §2~§3 참조.

---

## AC 체크리스트 (10건)

### 원본 AC (이슈 #42 본문)
- [x] `docs/specs/dev_spec.md` A5-1 Dual-Tier 재작성 — **#40(3cfafdb)에서 완료**
- [x] 발표 스토리 신규 작성 — **`docs/presentation/00_pitch_story.md` (374줄, #43 rebase 후 위치 변경)**
- [x] Track A/B 가치 제안 문서화 — **pitch_story §3 + dev_spec:874-898 인용**
- [x] 심사 Q&A 스크립트 — **pitch_story §8 (Q&A 8건)**
- [x] 후속 이슈 권고안 — **EXECUTION_PLAN.md §3.3 + 각 이슈 코멘트 (04_followup_issues.md 별도 파일 불필요)**
- [x] CLAUDE.md 경로 기재 — **§핵심 문서 위치에 presentation/, whitepaper/ 추가**
- [x] `docs/specs/.ai.md` 최신화 — **pitch_story 위치 + dev_spec v3.1 노트 추가**

### Scope 확장 AC (2026-04-08 코멘트 #1)
- [x] `docs/whitepaper/v1.0-moving-intelligence.md` v1.2 — **팩트 정정 + §6 확장 + 변경 이력**
- [x] `docs/whitepaper/v1.1-branding-strategy.md` v1.1.1 — **팩트 정정 완료**
- [x] `docs/whitepaper/.ai.md` 최신화 — **v1.2/v1.1.1 상태 + 규칙 추가**

### 추가 완료 (세션 중 발견·처리)
- [x] `docs/specs/dev_spec.md` S1 재정의 — OPEN_COUNT → CONTRACT_COUNT (주 선행), 변경 이력 §2026-04-09 추가
- [x] `docs/work/EXECUTION_PLAN.md` 전면 업데이트 — §2.3 "2-4주 선행" 검증 프레임워크, §3.3 백로그 매트릭스
- [x] GitHub Issue #46 생성 — 공공 데이터 통합 검증 파이프라인
- [x] `.omc/research/42-lead-time-verification.md` §H6 — KOSIS 교차검증 결과 기록
- [x] `docs/presentation/00_pitch_story.md` §4.2 Layer 2 — KOSIS 실측(r=0.002) + Option B 재프레이밍
- [x] `docs/presentation/00_pitch_story.md` §7 검증 프레임워크 — OPEN 물리 공리 기반으로 재작성

---

## 미완료 (잔존 작업)

### ~~Step 8. dev_spec.md 잔존 정정 2건~~ — **완료 (2026-04-09)**

| 항목 | 위치 | 결과 |
|---|---|---|
| B3-3 GET_SEGMENT_PROFILE 허위 문장 | L1571 | #40에서 이미 정정 완료 (L2977 변경 이력 확인) |
| A4-1 validate_move_signals S1 컬럼 | L723-729 | `OPEN_COUNT` → `CONTRACT_COUNT` 정정 (#42 S1 재정의 반영) |

### 최종 검증 통과

| 검증 항목 | 명령 | 기대값 |
|---|---|---|
| "주소변경" 잔존 | `rg -n "주소변경" docs/whitepaper/ docs/presentation/` | 변경 이력 인용 제외 0건 |
| RICHGO "인구이동" 잔존 | `rg -n "인구이동" docs/whitepaper/v1.0-moving-intelligence.md` | 0건 |
| {TBD} 잔존 | `rg -n "TBD" docs/presentation/00_pitch_story.md` | 0건 |
| Track A/B 표기 | `rg -n "Track A\|Track B" docs/presentation/00_pitch_story.md` | ≥ 10건 |

### 커밋 + PR

- **커밋 1** (메인): `feat: Dual-Tier 발표 스토리 + 기획서 v1.2 + KOSIS Option B 검증 프레임워크 (#42)`
- **커밋 2** (dev_spec 잔존): `refactor(devspec): B3-3/A4-1 잔존 정정 — #40 후속 (#42)`
- **PR**: master ← refactor/000042-dual-tier-pitch

---

## 핵심 결정 사항 (ADR)

### "2-4주 선행" 방어 전략 — Option B (2026-04-09 확정)

**배경**: KOSIS 주민등록 전입신고(DT_1B040A3) 교차검증 실행 결과 demeaned r=0.002 (p=0.949) — 통계적 유의성 없음.

**결정**: Option B — "이사 시점 = OPEN 시점" 물리 공리 기반 방어

| 레이어 | 근거 | 수치 |
|---|---|---|
| **Layer 1** (내부 실증) | CONTRACT → OPEN lag 1개월 | r=0.895, p<0.001, n=841 |
| **Layer 2** (공공 통계 구조 확인) | KOSIS는 구조적 후행 (D+30~D+45) → r≈0은 예측된 결과, 우리 가치의 역설적 증명 | r=0.002, p=0.949 |
| **Layer 3** (법률) | 주민등록법 §16 — 전입신고 이사 후 14일 이내 | 법정 기한 |
| **Layer 4** (upper bound) | 국토부 실거래가 계약~잔금 2~3개월 | 외곽 근거 |

**OPEN = 이사 당일 인터넷 설치 = 물리적 이사 시점의 공리**

**비즈니스 논리**: "KOSIS는 이사 완료 후 집계. 우리 CONTRACT는 이사 예약 단계. 공공 통계로 구조적으로 불가능한 선행성이 우리 가치."

### pitch_story 위치 — docs/presentation/00_pitch_story.md (2026-04-09 확정)

- `docs/specs/` 아닌 `docs/presentation/` (이슈 #43에서 신설된 디렉토리 규칙 정합)
- CLAUDE.md, .ai.md 모두 반영 완료

---

## 참조

- 실행 계획: `docs/work/EXECUTION_PLAN.md`
- 검증 연구: `.omc/research/42-lead-time-verification.md`
- 공공 데이터: `.omc/research/42-public-data-sources.md`
- 3구 프로파일: `docs/presentation/01_district_profiles.md` (#43)
- dev_spec Track A/B: `docs/specs/dev_spec.md:870-898`
