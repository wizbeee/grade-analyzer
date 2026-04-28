# CLAUDE.md — 성적 분석 프로그램 컨텍스트

## 프로젝트 개요
반·학년·전교 단위 집단 성적 분석 + 개인 진단 프로그램.
단일 HTML 파일(index.html) 아키텍처, 완전 오프라인 동작.

## 실행 방법
```bash
# 방법 1: http-server
npx http-server . -p 8091 --cors -c-1

# 방법 2: 파일 더블클릭 (index.html)
```

## 파일 구조
```
grade-analyzer/
├── index.html          ← 전체 프로그램 (HTML + CSS + JS, ~5500줄)
├── vendor/             ← 오프라인 라이브러리 (6.5MB, 커밋 포함)
│   ├── xlsx.full.min.js       (XLSX.js 0.18.5)
│   ├── chart.umd.min.js      (Chart.js 4.4.1)
│   ├── plotly.min.js          (Plotly.js 2.35.2)
│   └── html2pdf.bundle.min.js (html2pdf 0.10.1 + html2canvas)
├── CLAUDE.md           ← 이 문서
├── HANDOFF.md          ← 이전 버전 핸드오프 (참고용)
├── README.txt          ← 사용자 안내서
└── .gitignore
```

## 아키텍처 핵심
- **데이터 모델**: Long format (1행 = 1학생 × 1과목 × 1회차 × 1년도)
- **Wide 포맷 자동 변환**: 과목이 열 헤더인 엑셀 → Long 자동 펼침
- **전역 state 객체**: `state.parsedData`, `state.filters`, `state.analysisMode`, `state.theme`, `state.currentTab`
- **차트 레지스트리**: `const charts = {}` — 19개 차트 인스턴스, destroy() 후 재생성 패턴
- **setTimeout(0) 렌더링**: innerHTML 설정 후 차트 초기화 (rAF는 백그라운드 탭에서 작동 안 함)

## 구현 완료 기능

### 7개 분석 탭 (집단 모드)
| 탭 | ID | 주요 차트/기능 |
|---|---|---|
| 1. 전체 요약 | g-summary | KPI 4종, 과목별 테이블, 자동 인사이트, What-if 시뮬레이터 |
| 2. 점수 분포 | g-distribution | Plotly 히스토그램+정규곡선, 박스플롯, Chart.js 등급 누적 |
| 3. 과목 심층 | g-subject | 과목별 KPI, Plotly 히스토그램, 9등급 막대, 반비교, 상하위10 |
| 4. 집단 비교 | g-compare | 반/성별/계열 차원, ANOVA η², Plotly 박스플롯 |
| 5. 상관 관계 | g-correlation | Plotly 히트맵, 산점도+회귀선, 상관 해석 |
| 6. 추세 분석 | g-trend | Mode A(동일코호트)/B(다른코호트) 자동 감지, 년도별 추이 |
| 7. 학생 진단 | g-student | 레이더, 과목별 바, 회차/년도 라인, 반내 순위 |

### Phase 2 기능
- 필터 패널 (년도/회차/반/성별/계열 칩)
- What-if 시뮬레이터 (과목 ±20점 가상 조정)

### Phase 3 기능
- LocalStorage 프로젝트 저장/불러오기 (최대 20개)
- JSON 백업 내보내기/가져오기 (다른 PC 이동용)
- Excel 4시트/PDF/CSV/이미지 내보내기
- 명령 팔레트 (Ctrl+K, 20개 명령)
- 키보드 단축키 (1~7 탭이동, Ctrl+S/D/←/→, Shift+?)
- 도움말 모달
- 자동 인사이트 (5가지 지표)
- 샘플 데이터셋 3종 (group-mock/group-naesin/group-small)
- 다크 모드

### 엑셀 파싱
- **Long 포맷**: 과목/원점수 컬럼이 있는 세로형
- **Wide 포맷**: 국어/수학/영어... 과목이 열 헤더인 가로형 → 자동 감지 & 변환
- `KNOWN_SUBJECTS` (36종) + `COL_KEYWORDS` + `COL_BLACKLIST`로 정확 매핑
- 파싱 후 진단 패널 표시 (감지된 형식/컬럼 매핑/레코드 수)

## 주요 함수 위치 (검색 키워드)
- `renderGroupSummary` / `renderGroupSummaryCharts` — 탭 1
- `renderGroupDistribution` / `renderGroupDistributionCharts` — 탭 2
- `renderGroupSubject` / `renderGroupSubjectCharts` — 탭 3
- `renderGroupCompare` / `renderGroupCompareCharts` — 탭 4
- `renderGroupCorrelation` / `renderGroupCorrelationCharts` — 탭 5
- `renderGroupTrend` / `renderGroupTrendCharts` — 탭 6
- `renderGroupStudent` / `renderGroupStudentCharts` — 탭 7
- `processUploadedFiles` — 엑셀 파싱 메인 진입점
- `detectWideSubjectColumns` / `expandWideRow` — Wide 포맷 변환
- `normalizeRecord` / `findCol` — Long 포맷 컬럼 매핑
- `generateAutoInsights` — 자동 인사이트
- `onWhatIfChange` — What-if 시뮬레이터
- `exportProjectJson` / `importProjectJson` — JSON 백업
- `openCommandPalette` / `commandPaletteCommands` — 명령 팔레트
- `loadDemoData` — 샘플 데이터 생성

## 진로진학부 보고서 (15-시트 묶음 .xlsx 출력)
- **트리거**: 헤더 내보내기 메뉴 → "📑 진로진학부 보고서 (.xlsx)" / 명령 팔레트
- **함수**: `exportCounselReport()` → `CounselReport.buildAll(records)`
- **입력 파서**: `parseFormatA()` (예상등급컷 RAW 단일 헤더), `parseFormatB()` (통합양식 2행 병합 헤더, 학년도/표점/백분위 포함). `processUploadedFiles`에서 Wide/Long 폴백 전 우선 시도. 입력/저장 시트 등 중복은 dedup 단계에서 제거.
- **회차 메타**: 업로드 항목별 `sessionLabel` (3월/6월/9월/수능 등) — 직전평가 비교 시트 기준점
- **출력 시트** (학년·시점에 따라 자동 생략): 종합상위권 명단, (국어/수학/영어) 1등급 명단, 직전평가 비교(3학년), 사탐선택자 분석(3학년), 고대 최저 충족자(3학년), 국어/수학/영어/사탐/과탐/한국사 분석
- **계열 판정**: `classifyTanguTrack(탐구1, 탐구2)` — 둘 다 사회 → 문과, 둘 다 과학 → 이과, 그 외 혼합
- **참조 기준 파일**: `2026 3월 실채점결과 분석(진로진학부) 공유용.xlsx`

## 알려진 이슈 & TODO
- 사용자 실제 엑셀 데이터로 파싱 검증 필요 (컬럼명 변형 가능성)
- Wide 포맷에서 표준점수/백분위/등급 등 부가 데이터 추출 미지원 (원점수만)
- 개인 모드 탭은 기본 구현만 완료 (모의고사/내신 각 1탭)
- html2canvas 기반 이미지/PDF 내보내기는 복잡한 Plotly 차트에서 불완전할 수 있음

## 데이터 프라이버시
모든 처리가 브라우저 JavaScript에서 수행됨. 서버 전송 API 호출 없음.
vendor/ 라이브러리도 로컬 → CDN 연결 없음.
