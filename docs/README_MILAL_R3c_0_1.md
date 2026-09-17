# MILAL R3c.0.1

**MILAL = Marker-Informed Linguistic Analysis of Layers**

## Required inputs

Download 폴더에 다음 두 결과 ZIP이 필요합니다.

- `job_r3b_2_results.zip`
- `job_r3b_3_results.zip`

BHSA/Text-Fabric:

- `~/text-fabric-data/github/ETCBC/bhsa/tf/2021`

## Why both R3b.2 and R3b.3?

R3b.3은 lineage 계보를 보존하지만 반복 bundle의 모든 출현 위치를 다시 싣지 않습니다.
경계절에 걸리는 모든 형식을 복원하기 위해 R3b.2의 `03_bundle_occurrences.csv`가 필요합니다.

## Core changes from R3c.0

1. 모집단 = R3b.3 `09_lineage_review_workspace.csv`의 1,066 review containers.
2. `REPEATED_BUNDLE`, `SINGLETON_REFINEMENT_EVENT`, `G6_SINGLETON_REVIEW_ITEM` 분리.
3. 31:40 / 32:1 / 32:2 / 37:24 / 38:1 / 42:7은 대표 bundle 하나가 아니라 all-match control panel.
4. BHSA TF 2021에서 앞/현재/뒤 절, clause, sentence 문맥 재부착.
5. sequence-extension은 genealogy와 합치지 않고 별도 overlay.

## Main outputs

- `02_pilot_review_containers.csv`
- `03_pilot_container_repeated_bundles.csv`
- `04_pilot_container_singleton_refinement_events.csv`
- `05_pilot_container_g6_singleton_items.csv`
- `06_pilot_container_sequence_extension_overlay.csv`
- `07_pilot_review_container_packet.md`
- `08_boundary_control_pattern_matches.csv`
- `09_boundary_control_sequence_extension_overlay.csv`
- `10_boundary_control_panels.md`
- `11_tf_context_inventory.csv`
- `12_r3c_0_1_gates.csv`
- `13_method_note.md`
- `14_run_summary.json`
- `90_run_metadata.json`
- `99_manifest_sha256.csv`

## Self-test

```bash
python milal_r3c_0_1_reviewability.py --self-test
```

Self-test는 synthetic data를 사용하므로 BHSA가 필요하지 않습니다.
실제 run은 Text-Fabric/BHSA가 필요합니다.
