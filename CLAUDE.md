# CLAUDE.md — 성적 분석 프로그램 컨텍스트

## 프로젝트 개요
반·학년·전교 단위 집단 성적 분석 + 개인 진단 프로그램.
단일 HTML 파일(index.html, ~14k줄) 아키텍처, 완전 오프라인 동작.

## 실행 방법
```bash
# 방법 1: http-server
npx http-server . -p 8091 --cors -c-1

# 방법 2: 파일 더블클릭 (index.html)
```

## 파일 구조
```
grade-analyzer/
├── index.html          ← 전체 프로그램 (HTML + CSS + JS, ~14,200줄)
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

### 8개 분석 탭 (집단 모드)
| 탭 | ID | 주요 차트/기능 |
|---|---|---|
| 1. 전체 요약 | g-summary | KPI 4종, 과목별 테이블, 자동 인사이트, What-if 시뮬레이터 |
| 2. 점수 분포 | g-distribution | Plotly 히스토그램+정규곡선, 박스플롯, Chart.js 등급 누적 |
| 3. 과목 심층 | g-subject | 과목별 KPI, Plotly 히스토그램, 9등급 막대, 반비교, 상하위10 |
| 4. 집단 비교 | g-compare | 반/성별/계열 차원, ANOVA F+p값+η², **Tukey HSD 사후검정**, Plotly 박스플롯 |
| 5. 상관 관계 | g-correlation | Plotly 히트맵, 산점도+회귀선, **Pearson p값+95% CI+본페로니 보정** |
| 6. 추세 분석 | g-trend | Mode A(동일코호트)/B(다른코호트) 자동 감지, 년도별 추이 |
| 7. **교차 탐색** | **g-cross** | **NEW**: 9차원×9차원×6메트릭 자유 조합 히트맵, 셀 클릭 드릴다운 |
| 8. 학생 진단 | g-student | 레이더, 과목별 바, 회차/년도 라인, 반내 순위 |

### Phase 2 기능
- 필터 패널 (년도/회차/반/성별/계열 칩)
- What-if 시뮬레이터 (과목 ±20점 가상 조정)

### Phase 3 기능
- LocalStorage 프로젝트 저장/불러오기 (최대 20개)
- JSON 백업 내보내기/가져오기 (다른 PC 이동용)
- Excel 4시트/PDF/CSV/이미지 내보내기
- 명령 팔레트 (Ctrl+K, 25+ 명령)
- 키보드 단축키 (1~8 탭이동, Ctrl+S/D/←/→, Shift+?)
- 도움말 모달
- 자동 인사이트 (5가지 지표)
- 샘플 데이터셋 3종 (group-mock/group-naesin/group-small)
- 다크 모드

### Phase 4 기능 (분석 자유도 ↑)
- **드릴다운**: Chart.js 거의 모든 차트 클릭 → `wireDrilldownToCharts()`가 onClick 자동 주입 → 학생 명단 모달 (CSV export)
- **교차 탐색 탭(g-cross)**: 행/열/측정값 자유 조합 — `state.cross` + `buildCrossMatrix()` + 컬러 히트맵
- **사용자 정의 그룹** (`state.customGroups`): 학생 다중선택 → 색상·이름 그룹 → 사이드바 칩 토글 시 `state.filters.customGroups`로 전체 분석 좁힘. 별도 LocalStorage(`grade-analyzer-custom-groups-v1`)
- **차트 스튜디오** (`state.customCharts` + `state.chartStudio`): 16종 Plotly 차트(bar/line/area/pie/scatter/bubble/3d/radar/box/violin/histogram/heatmap/waterfall/funnel/treemap/sunburst) 자유 빌드 → 라이브러리 저장 → 보고서 PPT 부록 슬라이드 + Excel 이미지 시트로 자동 임베드. 별도 LocalStorage(`grade-analyzer-custom-charts-v1`)

### Phase 5 기능 (분석 정확도 ↑ — API 없음)
- **컬럼 통계 프로파일러** (`profileColumn`, `inferColumnRole`, `buildSheetSchema`): 데이터 분포·범위·유니크성으로 23개 역할 자동 추론. 헤더+데이터 이중 검증으로 신뢰도 0~1 산출
- **매핑 확인 모달**: 신뢰도 < 70% 컬럼 강조, 23개 역할 드롭다운 즉시 변경, **헤더 fingerprint 저장**(`grade-analyzer-mappings-v1`)으로 같은 양식 재업로드 시 자동 적용
- **데이터 품질 보고서**: 9개 필드 결측률, 과목별 IQR×1.5 이상치, 4종 일관성 위반(점수범위/등급범위/백분위범위/점수↔등급 모순)
- **고급 통계 (`StatTests`)**: lnGamma(Lanczos) → incBeta(연분수) → t분포·F분포·Pearson p값. 95% CI는 t/Fisher z 변환. **Tukey HSD 사후검정 + 본페로니 보정**으로 다중비교 위양성 방지

### 엑셀 파싱
- **Long 포맷**: 과목/원점수 컬럼이 있는 세로형
- **Wide 포맷**: 국어/수학/영어... 과목이 열 헤더인 가로형 → 자동 감지 & 변환
- `KNOWN_SUBJECTS` (36종) + `COL_KEYWORDS` + `COL_BLACKLIST`로 정확 매핑
- 파싱 후 진단 패널 표시 (감지된 형식/컬럼 매핑/레코드 수)

## 주요 함수 위치 (검색 키워드)
- `renderGroupSummary` / `renderGroupSummaryCharts` — 탭 1
- `renderGroupDistribution` / `renderGroupDistributionCharts` — 탭 2
- `renderGroupSubject` / `renderGroupSubjectCharts` — 탭 3
- `renderGroupCompare` / `renderGroupCompareCharts` — 탭 4 (ANOVA p값 + Tukey HSD)
- `renderGroupCorrelation` / `renderGroupCorrelationCharts` — 탭 5 (Pearson p값 + 본페로니)
- `renderGroupTrend` / `renderGroupTrendCharts` — 탭 6
- `renderGroupCross` / `renderGroupCrossCharts` — 탭 7 (NEW: 자유 교차)
- `renderGroupStudent` / `renderGroupStudentCharts` — 탭 8
- `processUploadedFiles` — 엑셀 파싱 메인 진입점
- `detectWideSubjectColumns` / `expandWideRow` — Wide 포맷 변환
- `normalizeRecord` / `findCol` — Long 포맷 컬럼 매핑 (legacy 키워드 기반)
- `profileColumn` / `inferColumnRole` / `buildSheetSchema` — NEW: 데이터 기반 자동 추론
- `openSmartMapping` / `applyMappingTemplate` / `loadMappingTemplates` — NEW: 매핑 모달 + fingerprint
- `normalizeRecordSchema` — NEW: 사용자 확정 스키마로 정규화
- `runDataQuality` / `openDataQuality` — NEW: 결측·이상치·일관성 보고서
- `StatTests` (`pTTwo`, `pFOne`, `pPearson`, `tukeyHSD`, `welchT`, `cohensD`, `meanCI`) — NEW: 정확 p값/효과크기/CI
- `wireDrilldownToCharts` / `drilldownByLabels` / `openDrilldown` — NEW: 차트 클릭 드릴다운
- `openChartStudio` / `buildPlotlyChart` / `renderCustomChartsToImages` — NEW: 16종 차트 빌더
- `openGroupManager` / `toggleGroupFilter` — NEW: 사용자 정의 그룹
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

## 학교 기수↔학년도 기준선
파일명에 "20xx" 4자리 학년도가 없어도 "N기" 패턴으로 자동 매핑하기 위한 baseline.
`SCHOOL_KISU_BASELINE = { kisu: 13, year: 2026 }` (index.html 상단, `detectYearFromFilename` 위).
다른 학교/연도로 이동 시 이 한 줄만 수정. 매핑 공식: `year = baseline.year + (N - baseline.kisu)`.
검증된 입력 양식 6종: 8~10기 (기수 컬럼만), 11~12기 (학년도+기수), 13기 (학년도만, 시트명 "empty") — 모두 `parseFormatB`가 자동 인식.

## 다른 PC 이동 가이드
1. **코드 이식**: `git clone https://github.com/wizbeee/grade-analyzer.git` 또는 GitHub에서 ZIP 다운로드
2. **데이터 이식**: 사이드바 → 프로젝트 관리 → "전체 백업" 클릭 → `.json` 파일 다운로드 → 다른 PC에서 같은 모달의 "백업 불러오기" 클릭
3. **매핑 양식 이식**: LocalStorage 4개 키(`gradeAnalyzer:project:current`, `grade-analyzer-custom-charts-v1`, `grade-analyzer-custom-groups-v1`, `grade-analyzer-mappings-v1`)는 백업 JSON에 일부 포함. 차트/그룹/매핑 양식까지 옮기려면 DevTools → Application → LocalStorage에서 별도 export 필요.

## 알려진 이슈 & TODO
- Wide 포맷에서 표준점수/백분위/등급 등 부가 데이터 추출 미지원 (원점수만)
- 개인 모드 탭은 기본 구현만 완료 (모의고사/내신 각 1탭)
- html2canvas 기반 이미지/PDF 내보내기는 복잡한 Plotly 차트에서 불완전할 수 있음
- 매핑 모달 자동 트리거 미통합: `parseFormatA/B + Wide/Long`이 모두 실패해도 모달은 자동으로 뜨지 않음. 사용자가 사이드바 "매핑 다시 확인" 메뉴로 수동 호출. 통합 시 `processUploadedFiles`에 4번째 파싱 경로 추가 필요.

## 데이터 프라이버시
모든 처리가 브라우저 JavaScript에서 수행됨. 서버 전송 API 호출 없음.
vendor/ 라이브러리도 로컬 → CDN 연결 없음.
