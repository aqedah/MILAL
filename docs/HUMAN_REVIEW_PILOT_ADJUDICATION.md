# MILAL 30-case Human Review Pilot — Human-authored adjudication

이 문서와 companion CSV는 사용자가 직접 수행한 인간 판정의 공식 원자료(human-authored source-of-truth)이다. R3c/PROV1 자동 산출물이나 알고리즘 판정이 아니다.

## Provenance

- cases: CASE001–CASE030
- source: human researcher adjudication
- date: 2026-09-21
- automated_judgment: none
- review_time_measurement: not measured
- structural_rhetorical_function_labels: not automatically assigned
- form_assessment_provenance: human-authored adjudication value
- source_document_sha256: 1de93dd7cf524de5ab9bf9e0c4450d5715aee0649b32aa021069152f63a360f4
- baseline_commit: 8c87fc33f612326eca0ee2ed0b8781451297c85b

원문 출처: 사용자가 제공한 2026-09-21 작업 지시의 §4 판정 및 §5 종합 관찰. 위 SHA256은 해당 첨부 원문 바이트를 식별한다.
`form_assessment`는 이번 human pilot 기록을 위한 human-authored adjudication value이며 새로운 MILAL 자동 라벨이 아니다. 본문의 경계·기능·연속성에 관한 서술도 인간 연구자의 판정 원문이다.
`review_status`는 사용자 지시에 따라 전부 `REVIEWED`이다. `review_time_seconds`는 측정하지 않았으므로 CSV에서는 빈 셀, 아래에서는 `[blank]`로 표기한다.
각 case의 판정 설명은 원문 문장 및 순서를 유지하여 `reviewer_notes`에 전부 기록했다. 사용자가 개별 필드로 배정하지 않은 `observable_behavior`, `recurring_context`, `exceptions`, `additional_information_needed`는 비워 두었다. 이는 관찰이나 예외가 없다는 판정이 아니다.
`case_type`은 baseline commit의 `src/milal_r3c_1_review_units.py`에 정의된 `CASE_TYPES` 및 case 생성 순서(각 6개)에 따른 기존 pilot metadata이다. 새로운 분석 분류나 재표집은 수행하지 않았다.
CASE001–006: HIGH_OCCURRENCE_BUNDLE; CASE007–012: LOW_OCCURRENCE_BUNDLE; CASE013–018: RANDOM_BUNDLE; CASE019–024: SINGLETON_OUTCOME; CASE025–030: BOUNDARY_CONTROL.
CSV의 공통 provenance 열은 이 절의 값을 각 행에 반복한다. 두 파일의 case 판정은 동일하다.
이 기록은 Git으로 공유한다. inputs/results, R3c/PROV1 결과 및 기존 인간 판정 필드에 writeback하지 않는다.

## Case adjudications

### CASE001

- case_id: CASE001
- case_type: HIGH_OCCURRENCE_BUNDLE
- form_assessment: INSUFFICIENT
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 동일 `xYq0`라는 계산적 공통성은 재현되지만 366개 표면형은 지나치게 이질적이다.
  - 저해상도 baseline class로는 보존 가능하나 하나의 인간 인식 가능 형식으로 보기 어렵다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE002

- case_id: CASE002
- case_type: HIGH_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 명사문이라는 명확한 언어학적 공통성을 가진다.
  - 구조적 유용성은 별도 문제다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE003

- case_id: CASE003
- case_type: HIGH_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - CASE002의 명사문 중 verbal morphology가 없는 307개가 남는 refinement는 자연스럽다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE004

- case_id: CASE004
- case_type: HIGH_OCCURRENCE_BUNDLE
- form_assessment: INSUFFICIENT
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 동일 `ZYq0`라는 분류 근거는 이해되지만 표면적으로 하나의 일관된 형식으로 인식하기 어렵다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE005

- case_id: CASE005
- case_type: HIGH_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - `WxY0` 계열의 공통성이 표면적으로 비교적 눈에 띈다.
  - 다만 관찰되는 `וְ` 하나로 전체 유형을 환원하지 않는다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE006

- case_id: CASE006
- case_type: HIGH_OCCURRENCE_BUNDLE
- form_assessment: INSUFFICIENT
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 동일 `xQt0`라는 계산적 공통성은 재현되지만 실제 예문은 인간에게 이질적이다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE007

- case_id: CASE007
- case_type: LOW_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 1:7과 2:2의 4-clause_atom sequence가 명확하게 반복된다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE008

- case_id: CASE008
- case_type: LOW_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - CASE007의 동일 반복이 여호와의 다음 발화 공식까지 5단위로 자연스럽게 연장된다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE009

- case_id: CASE009
- case_type: LOW_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 반복이 6단위까지 유지되며 두 하늘 장면의 형식적 병행이 뚜렷하다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE010

- case_id: CASE010
- case_type: LOW_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 동일 sequence가 7단위까지 연장된다.
  - CASE007–009와 독립적 증거로 중복 계산하지 않는다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE011

- case_id: CASE011
- case_type: LOW_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 욥에 대한 동일 평가까지 포함하여 8단위 병행이 유지된다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE012

- case_id: CASE012
- case_type: LOW_OCCURRENCE_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 작은 전치사 차이에도 9단위 장면 병행은 명확하다.
  - CASE007–012는 하나의 확장 sequence 계열로 이해한다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE013

- case_id: CASE013
- case_type: RANDOM_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 동일 verbal morphology 11개 중 `접속 + 부정 + 동사` 구성 3개가 G2에서 남는 과정이 자연스럽다.
  - G3에서는 빈 core-argument component `[]`가 추가되어도 세 occurrence가 유지되고, G4의 동사 lexeme에서 분리된다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE014

- case_id: CASE014
- case_type: RANDOM_BUNDLE
- form_assessment: PARTIAL
- sufficient_context: PARTIAL
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 두 clause_atom 배열을 형식적 집단으로 볼 수 있다.
  - 다소 추상적이지만 히브리 시의 평행법을 고려하면 이해 가능하다.
  - 그러나 실제 평행 기능을 주장하려면 문맥 검토가 필요하다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE015

- case_id: CASE015
- case_type: RANDOM_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - `접속 요소 + 명사적 표현`이라는 형식이 눈에 들어오며 26개에서 12개로 좁아지는 과정도 납득된다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE016

- case_id: CASE016
- case_type: RANDOM_BUNDLE
- form_assessment: INSUFFICIENT
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 동일 기본 문장형과 Piel 미완료 2ms라는 형태론적 공통성은 있으나 하나의 반복 형식으로 보기에는 추상적이다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE017

- case_id: CASE017
- case_type: RANDOM_BUNDLE
- form_assessment: PARTIAL
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 비동사 서술이라는 넓은 공통성은 있으나 52개 내부의 실제 형식이 다양하다.
  - 인간 판정상 INSUFFICIENT에 가까운 PARTIAL 사례다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE018

- case_id: CASE018
- case_type: RANDOM_BUNDLE
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - `비동사형 문장 → 2ms Qal 명령`이라는 두 단위 연쇄는 실제로 눈에 띈다.
  - 동일한 담화 기능 여부는 문맥에서 별도로 판단한다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE019

- case_id: CASE019
- case_type: SINGLETON_OUTCOME
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - S02135는 G2까지 Job 19:14와 동일하지만 G3의 subject NP word-class realization 차이로 count가 2→1이 된다.
  - singleton 이유가 실제 본문에서 확인된다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE020

- case_id: CASE020
- case_type: SINGLETON_OUTCOME
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 같은 부정사/명사구 계열 6개 중 명사구의 성·수·구성을 추가하면서 Job 17:6이 하나로 갈리는 과정은 자연스럽다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE021

- case_id: CASE021
- case_type: SINGLETON_OUTCOME
- form_assessment: PARTIAL
- sufficient_context: PARTIAL
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 9:4가 두 동사형 조합 때문에 singleton이 되는 이유는 설명 가능하다.
  - 그러나 그 유일성은 우연한 형태론 조합일 가능성이 있다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE022

- case_id: CASE022
- case_type: SINGLETON_OUTCOME
- form_assessment: PARTIAL
- sufficient_context: PARTIAL
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 22:7이 constituent 배열 때문에 singleton이 되는 과정은 이해된다.
  - 독특한 형식인지 우연한 희귀 조합인지는 애매하다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE023

- case_id: CASE023
- case_type: SINGLETON_OUTCOME
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 35:3의 `의문사 + 동사 + 전치사구` 배열은 구체적이며 singleton 형성 이유가 명확하다.
  - 형식적 유일성과 구조적 중요성은 구분한다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE024

- case_id: CASE024
- case_type: SINGLETON_OUTCOME
- form_assessment: PARTIAL
- sufficient_context: PARTIAL
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - 두 4단위 sequence가 같은 morphology 골격을 공유하다 constituent shape에서 갈라지는 refinement는 납득된다.
  - Job 42 문맥에서 실제 서술 패턴인지 확인이 필요하다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE025

- case_id: CASE025
- case_type: BOUNDARY_CONTROL
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 31:40 `תמו דברי איוב`은 욥 발화의 명확한 종결 경계다.
  - 관련 23개 unit을 하나의 대표 pattern으로 축소하지 않는 방식이 적절하다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE026

- case_id: CASE026
- case_type: BOUNDARY_CONTROL
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 32:1은 31:40의 종결을 이어받아 친구들의 응답 중단을 명시하고 32:2로 넘기는 전환절로 보는 것이 자연스럽다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE027

- case_id: CASE027
- case_type: BOUNDARY_CONTROL
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 32:2는 엘리후 등장부의 명확한 시작이다.
  - `31:40 종결 → 32:1 기존 논쟁 종결/전환 → 32:2 엘리후 도입`의 흐름이 자연스럽다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE028

- case_id: CASE028
- case_type: BOUNDARY_CONTROL
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 37:24는 엘리후 연설의 명확한 종결점이다.
  - 그러나 이것이 엘리후→여호와의 직접 담화 연속성을 의미하지는 않는다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE029

- case_id: CASE029
- case_type: BOUNDARY_CONTROL
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 38:1은 여호와 연설의 명확한 시작점이다.
  - `ויען יהוה את־איוב`이므로 명시적 수신자는 욥이다.
  - 엘리후 발화를 단순히 이어받는 것으로 해석하지 않는다.
- review_status: REVIEWED
- review_time_seconds: [blank]

### CASE030

- case_id: CASE030
- case_type: BOUNDARY_CONTROL
- form_assessment: CLEAR
- sufficient_context: YES
- observable_behavior: [blank]
- recurring_context: [blank]
- exceptions: [blank]
- additional_information_needed: [blank]
- reviewer_notes:
  - Job 42:7은 하나님–욥 대화를 닫고 하나님–친구들 장면을 시작하는 명확한 전환이다.
  - `ויהי אחר דבר...`도 이 전환을 뒷받침한다.
- review_status: REVIEWED
- review_time_seconds: [blank]

## 종합 결과

| form_assessment | Cases |
|---|---:|
| CLEAR | 21 |
| PARTIAL | 5 |
| INSUFFICIENT | 4 |

| sufficient_context | Cases |
|---|---:|
| YES | 26 |
| PARTIAL | 4 |
| NO | 0 |

30개 모두 REVIEWED; review_time_seconds는 30개 모두 blank / not measured.

## 인간 연구자의 방법론적 관찰

1. 같은 signature 또는 희귀성 자체는 구조적 중요성을 의미하지 않는다.
2. 긴 sequence 반복은 저수준 단일 clause-type family보다 인간에게 훨씬 명확하게 인식된다.
3. singleton은 “왜 유일한가”와 “그 유일성이 구조적으로 의미 있는가”를 구별해야 한다.
4. boundary evidence는 형식적 증거와 문맥이 함께 갈 때 강한 판정을 제공한다.
5. boundary와 discourse continuity는 동일하지 않다.
6. 특히 Job 37:24–38:1은 경계는 명확하지만 엘리후→여호와의 직접 담화 연속성을 자동으로 입증하지 않는다.
