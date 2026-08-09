# AneuX preprocessing-orbit candidate audit

상태: **historical 34/40 source shortlist · exact CPU-only P0
execution-incomplete/no scientific verdict · candidate closed · primary
problem/method/architecture/GPU/outer test 0**
기준일: 2026-08-09 KST

## 냉정한 결론

이번 fresh batch에서 admission line을 넘은 후보는 **same-lesion preprocessing
orbit quotient morphometry**다. AneuX는 같은 병변에 원본, 0.01 mm²,
0.05 mm² target-cell-area mesh와 dome/ninja/cut1/cut2 isolation을 제공한다.
이들을 서로 다른 환자나 data augmentation으로 세지 않고, 하나의 해부학을
관측하는 전처리 궤도

\[
  \mathcal O_i=\{X_{i,r,c}:r\in\mathcal R,\ c\in\mathcal C_i\}
\]

로 둔다. 후보 질문은 surface functional 또는 향후 예측기 \(f\)가 같은 병변의
궤도에서 얼마나 달라지는지, 그리고 그 nuisance를 quotient하면서 실제 병변 간
형태 차이를 보존할 수 있는지다.

그러나 **remeshing robustness, consistency loss, DiffusionNet, PointNet/GNN,
E(3) equivariance 또는 rupture-status classifier는 novelty가 아니다.** AneuX
원 연구는 morphometry의 mesh-quality robustness와 cut 선택을 이미 논했고,
MATCH는 segmentation/reconstruction variability를, DiffusionNet은 surface
discretization robustness를 직접 다뤘다. 2026 latent-shape 연구는 958개 aneurysm을
700/3k/12k correspondence mesh로 학습해 resolution robustness까지 보고했다.
따라서 남을 수 있는 gap은 단순 robust backbone이 아니라, **의료 전처리 궤도를
명시적 equivalence class로 두고 casewise functional 보존과 source-held-out
discrimination을 동시에 검증하는 정확한 quotient construction**뿐이다. 이것도
P0와 별도 method-free P1에서 비자명성이 확인될 때만 method 후보가 된다.

## 동일 척도의 fresh 후보 비교

각 축은 0--5점이고 admission line은 32/40이다. 점수는 논문 acceptance 확률이
아니라 현재 공개 자산으로 식별·반증 가능한 ISBI 문제인지에 대한 보수적
source score다.

| 후보 | 중요성 | 식별성 | 남은 gap | 자산 | 단위 | baseline | figure | 일정 | 합계 | 판정 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Same-lesion preprocessing-orbit quotient morphometry | 4 | 5 | 2 | 5 | 5 | 5 | 4 | 4 | **34** | P0-only shortlist |
| Source-stable rupture-status association | 4 | 2 | 2 | 5 | 4 | 5 | 4 | 4 | 30 | reject |
| Probabilistic neck/cut delineation | 4 | 4 | 1 | 4 | 4 | 5 | 5 | 4 | 31 | reject |
| Multi-aneurysm patient-set morphology | 3 | 3 | 2 | 4 | 2 | 4 | 3 | 4 | 25 | reject |
| Latent shape space across resolution | 3 | 4 | 0 | 5 | 5 | 5 | 4 | 4 | 30 | direct-prior reject |
| Membrane-equilibrium wall reconstruction | 5 | 1 | 2 | 1 | 2 | 3 | 5 | 2 | 21 | target/data reject |

Source-stable status association은 cohort selection과 label shift 때문에 stable
estimand를 식별하기 어렵고 generic domain generalization과 구분되지 않는다.
Neck posterior는 MATCH, automated isolation, 2026 NeckSpline과 AneuSI가 직접
가깝다. Patient-set 후보는 공개 patientID가 85% row에만 있고 다병변 환자 수가
작다. Latent shape space는 2026 direct paper가 사실상 문제를 점유했다.
Membrane-equilibrium reconstruction은 wall tension/thickness ground truth가 없어
물리 loss의 정답성을 평가할 수 없다. 이 후보들을 loss나 이름만 바꿔 되살리지
않는다.

## P0에서만 확인할 것

Frozen contract는
[`configs/aneux_preprocessing_orbit_p0.json`](../configs/aneux_preprocessing_orbit_p0.json)이다.
등록 전에는 official record, content-description, 논문과 code README만 읽었고,
`data-v1.0.zip`의 CSV payload, `models-v1.0.zip` central directory와 어느 mesh
member도 읽지 않았다.

P0는 `introai9` PBS의 4 CPU/16 GB/GPU 0에서 다음을 all-or-none으로 검사한다.

라이선스 표기는 서로 다르다. Official GitHub README는 CC BY 4.0이라고 쓰지만,
실제 v1.0 파일을 배포하는 Zenodo record metadata와 terms는 **CC BY-NC 4.0** 및
지정 문구·논문 인용을 요구한다. 이 프로젝트는 배포 record의 더 엄격한 조건을
적용하며 raw/compact geometry나 clinical table을 공개 저장소에 재배포하지 않는다.

1. 12,992,074-byte tabular ZIP과 MD5를 확인하고 clinical, clinical-per-cut,
   morpho-per-cut 세 CSV만 private cache에서 읽는다.
2. 750 unique lesion, source별 350/135/164/101, status 735, patientID 637 row와
   최소 450개 source-qualified observed patient group을 확인한다.
3. clinical-per-cut과 morphometry의 `(dataset, cutType)` key가 중복 없이 같고,
   네 cut이 존재하며 모든 lesion에 dome+ninja가 있는지 검사한다.
4. area-005 morphometry가 index를 제외하고 정확히 170 feature인지 확인한다.
5. 6,277,720,483-byte model ZIP은 HEAD, tail과 central directory exact byte
   range만 읽는다. Full archive와 VTP/STL/JSON/CSV member payload는 읽지 않는다.
6. central directory가 안전하고 세 resolution·네 cut token과 최소 4,500개
   aneurysm VTP member를 포함하는지 aggregate로만 확인한다.
7. case identifier, case-level value와 member listing은 공개하지 않고 listing
   SHA-256과 count만 남긴다.

네트워크 불안정이 과학 판정으로 오염되지 않도록 한 exact PBS job 안에서만
각 HTTP operation마다 0/10/30초 backoff의 최대 세 transport attempt를 결과
전에 고정했다. Retry는 timeout, connection reset, HTTP 408/429/5xx에만
허용한다. Parser/contract
failure는 반복하지 않고, 같은 source commit의 PBS 재제출도 금지한다. 이는
development repair round가 아니라 하나의 frozen transport procedure다.

P0 pass는 **method-free P1 등록만** 허용하도록 고정했다. Primary problem,
architecture, GPU와 outer test를 열지 않는다. P0 fail이면 candidate version을
닫고, 실행 불완료면 scientific verdict 없이 보존한다.

## 실제 P0 실행과 판정

Exact public source `42cc3c7127f382b440f2ac22f662c45692f37863`을 clean
checkout으로 확인한 뒤 `introai9`의 PBS job `115177.ECE-util1`에서 CPU 4개,
16 GB, GPU 0으로 정확히 한 번 실행했다. Scheduler는 exit 2, walltime
`00:37:00`, CPU time `00:00:00`, peak memory `26596kb`, run count 1을 기록했다.
생성된 aggregate의 error code는 `transport_attempts_exhausted`다.

실행은 첫 `data-v1.0.zip` transport operation의 동결된 세 attempt를 소진하기
전에 완성된 tabular archive를 만들지 못했다. 종료 시 completed/partial cache
file은 0이고 CSV member는 parse되지 않았다. 따라서 patient grouping,
cut–morphometry mapping, source/status count와 feature count를 포함한 tabular
check에 도달하지 않았다. Model ZIP의 HEAD/range, central directory와 member
payload도 전부 미접근이다. Transient transport byte를 일부 수신했는지는
aggregate로 식별하지 않으며, retained payload가 없었다는 사실만 기록한다.

13개 scientific asset check는 모두 **미평가**다. 이는 AneuX asset이나
preprocessing-orbit 가설의 fail이 아니다. 동시에 frozen no-resubmission
계약에 따라 transport/reader repair, same-contract rerun, P1, method,
architecture, GPU와 outer test를 열지 않고 이 candidate version을 닫는다. 공개
provenance는
[`results/aneux_preprocessing_orbit_p0_execution_20260809.json`](../results/aneux_preprocessing_orbit_p0_execution_20260809.json)에
있다.

## P0가 통과했다면 필요했을 P1 · 미등록/미실행

P1은 등록하지 않았다. P0가 통과했다면 결과 전에 별도 commit에서 다음을
수치화해야 했다.

- patient/source group을 보존한 deterministic geometry subset과 sampling rule
- rigid alignment 뒤 same-lesion cross-resolution/cross-cut surface discrepancy
- area, volume, NSI, curvature/writhe 계열의 casewise rank reversal과 uncertainty
- analytic area-weighted functional, precomputed morphometry, PointNet++,
  DiffusionNet과 E(3)-equivariant mesh model의 matched controls
- 동일 lesion orbit 내 variation과 lesion 간 variation의 분리
- source-held-out 평가와 status를 미래 risk로 읽지 않는 secondary analysis

P1에서 strong continuous/discretization-agnostic baseline이 이미 안정적이거나
orbit variation이 biological between-case margin에 비해 작으면 후보를 닫는다.
비자명한 failure가 있더라도 generic consistency penalty를 method로 채택하지
않는다. Operator-specific 또는 quotient-specific algorithm과 보장은 그 뒤의
새 development protocol에서만 설계한다.

## 직접 선행과 claim boundary

- [AneuX official dataset record](https://zenodo.org/records/6678442): 750 dome,
  668 vessel tree, 3 source, 3 mesh resolution, 4 cut, 170 morphometric index.
- [Shape trumps size](https://doi.org/10.3389/fneur.2022.809391): AneuX의
  morphometry, cut robustness와 external-source generalization failure.
- [MATCH geometry uncertainty](https://pmc.ncbi.nlm.nih.gov/articles/PMC6434802/):
  segmentation/reconstruction group variability에 따른 geometric-parameter UQ.
- [DiffusionNet](https://arxiv.org/abs/2012.00888): surface resolution과 sampling에
  robust한 discretization-agnostic learning.
- [AneuX PointNet++ status classifier](https://pubmed.ncbi.nlm.nih.gov/38426204/):
  dome/cut1 point cloud와 source external validation.
- [Latent shape space, 2026](https://doi.org/10.1016/j.cmpb.2026.109445):
  958 surface, uniform correspondence와 700/3k/12k latent model.
- [Sources of reconstruction variability, 2026](https://doi.org/10.1007/s13239-026-00841-1):
  software, threshold와 user가 100 IA의 reconstructed geometry를 바꾸는 분석.
- [NeckSpline](https://pubmed.ncbi.nlm.nih.gov/41998109/): centerline-aware
  differentiable continuous aneurysm-neck delineation.
- [AneuSI](https://doi.org/10.1016/j.cmpb.2026.109525): aneurysm/neck isolation의
  빠른 자동화와 manual comparison.

## 최종 판정

- Active source shortlist와 selected primary problem은 모두 0개다.
- P0는 한 번 실행됐지만 initial tabular transport exhaustion으로 scientific
  gate 전에 종료됐다. Complete/partial archive, CSV parse와 model range/member
  access는 0이다.
- 현재 모델은 GNN도 DiffusionNet도 아니며 architecture가 없다.
- GPU job은 0개이고, `junjinyong`은 어떤 접속·제출·조회에도 사용하지 않는다.
- 같은 source의 repair/rerun과 P1은 금지한다. 다음 작업은 별도의 fresh
  problem-level primary-source/asset audit이다.
