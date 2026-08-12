# ADAM patch-fold release와 2026 segmentation prior 재평가

> **판정 · 2026-08-12:** 실제 61.5 GB GitHub release가 새로 확인됐지만,
> 크기는 provenance·license·patient grouping을 대신하지 않는다. 작은 공개
> organization manifest는 ADAM positive scan 93개를 58개 base ID로 나누며,
> official ADAM의 B/F same-subject semantics를 적용하면 모든 fold에서 development와
> test 사이에 같은 subject base가 겹친다. DINO-3DRA, GeoP2VNet, modality-agnostic
> nnU-Net와 anatomy-aware weak supervision은 오히려 generic segmentation model
> novelty를 더 좁힌다. 여섯 후보는 **26.5/26.5/26.0/25.5/23.0/23.0**으로 모두
> 기각한다. Schema 10.7의 current primary batch, active lead, E0/P0/P1, method,
> architecture, scientific server, PBS/GPU, outer test와 manuscript claim은 바뀌지
> 않는다.

## 1. 무엇이 실제로 새로 공개됐는가

[Exact repository](https://github.com/josedaviddr/Aneurysm_segmentation_DataSet_folds/tree/d36df7d19a96aa5b9fca0cc9050e021ac7319fee)는
`v1.0` release에서 35개 split-tar part를 제공한다. Payload는 열지 않았고 GitHub
API metadata와 12,859-byte `folds_data_organization.json`만 읽었다.

| 항목 | 확인값 |
|---|---:|
| exact public head | `d36df7d19a96aa5b9fca0cc9050e021ac7319fee` |
| release | `v1.0`, release ID 349278633 |
| asset | 35 part |
| 합계 | 61,506,611,200 bytes |
| canonical name/size/digest manifest SHA-256 | `7d5ebe80859b4d781a13a3c1b65d3b18fb2dfa2bd13486bb64c36b980b133f9c` |
| repository license | 없음 |
| citation | manuscript title만 있고 journal/DOI는 `To be added` |
| declared dataset | ADAM |

이 release는 허구의 링크가 아니라 실제 material signal이다. 그래서 asset
manifest 자체는 source-watch v18에서 immutable contract로 고정한다. 그러나
repository가 upstream ADAM redistribution permission, challenge reuse approval,
source-image provenance와 새 dataset license를 제시하지 않는다. 공개 다운로드
가능성과 lawful research-use contract는 같은 말이 아니다. AURORA는 61.5 GB
payload를 내려받거나 archive member를 열지 않는다.

## 2. fold라는 이름이 patient-disjoint test를 뜻하지 않는다

Organization JSON은 validation ID 없이 train/test ID만 기록한다.

| fold | train scan ID | validation ID | test scan ID | exact ID overlap | B/F base-ID overlap |
|---:|---:|---:|---:|---:|---:|
| 0 | 74 | 0 | 19 | 0 | 2 (`10048`, `10050`) |
| 1 | 74 | 0 | 19 | 0 | 3 (`10048`, `10050`, `10059`) |
| 2 | 74 | 0 | 19 | 0 | 5 (`10056`, `10059`, `10061`, `10065`, `10066`) |
| 3 | 75 | 0 | 18 | 0 | 6 (`10056`, `10061`, `10065`, `10066`, `10069`, `10074`) |
| 4 | 75 | 0 | 18 | 0 | 2 (`10069`, `10074`) |

다섯 test union은 93개 exact scan ID를 각각 한 번씩 포함한다. 이 점만 보면
scan-level cross-validation은 정돈돼 있다. 하지만 ID는 B 35개, F 35개,
suffix 없는 ID 23개이고 suffix를 제거하면 58개 base가 된다. 이는 official
[ADAM challenge paper](https://doi.org/10.1016/j.neuroimage.2021.118216)의
training 구성—35 baseline/follow-up pair와 23 additional positive subject—과
정확히 일치한다.

따라서 **official B/F pairing semantics를 적용한 추론**으로는 표의 base overlap이
same-subject development/test overlap이다. 이는 source result 전체가 무효라는
주장이 아니다. Raw image와 patch archive를 열지 않았으므로 pixel duplication,
patch construction 또는 manuscript result를 단정하지도 않는다. 다만 patient-
grouped generalization을 주장하는 AURORA outer test로는 부적격이다.

추가로 manifest는 ADAM positive scan 93개만 열거한다. Official training의 negative
20건이 이 fold contract에 없으므로 whole-volume detection specificity나 FP/case를
평가하는 공개 contract도 아니다. README가 train/validation/test directory를
설명해도 organization JSON에는 validation ID가 없다. Archive 내부 구조를 열기
전에는 validation provenance를 확인했다고 쓰지 않는다.

## 3. 2026 segmentation architecture 공간은 이미 혼잡하다

### DINO-3DRA

[Exact head](https://github.com/JiayangDS/Dino3DRA/tree/5d9982ee794b531a8f04e73e849af0040976381f)는
frozen DINOv3 2D feature를 3D U-Net에 투영하는 inference code, 한 3DRA sample과
134-byte Git-LFS weight pointer를 제공한다. README는 5.72M trainable parameter와
세 independent dataset의 failure 제거를 보고하지만 arXiv identifier는 placeholder다.
Release, training driver, exact folds와 completed evaluation outputs는 없다. 이는
2026-08-12 현재 **repository-reported submission claim**이지 AURORA가 재현한 결과나
확인된 proceedings evidence가 아니다. 그래도 2D foundation feature를 3DRA로
주입하는 architecture novelty를 새로 주장하기 어렵게 만드는 direct-prior risk다.

### GeoP2VNet

[Exact head](https://github.com/somtiannes/GeoP2VNet/tree/25c59bc172d0fedac37c1b6cfc8fe4af0823bf65)는
vessel-surface descriptor, Gaussian point-to-voxel splatting과 gated fusion을
Swin-UNETR에 결합한다. Repository는 205 CTA/266 lesion five-fold result를
보고하고 training/evaluation code를 제공하지만 clinical dataset과 checkpoint는
없고 patient-grouped fold semantics도 공개하지 않는다. 수치는 AURORA result가
아니다. 명시적 geometry prior를 voxel segmentation에 결합하는 방향은 이미 직접
점유돼 있다.

### modality, weak supervision, anatomy prior

[Modality-agnostic code](https://github.com/Yuchen-Qiu-umcutrecht/Modality-Agnostic-for-Aneurysm-Segmentation/tree/8ae1eec763d87887dac728d591c2c2b6df36be4f)는
unpaired CTA/MRA shared nnU-Net, alternating modality batches, optional centroid
prior와 candidate-level FP filtering을 이미 구현한다. Repository-level license,
release, cohort table, frozen folds와 reported result table은 없다.

[Anatomy-aware weak-supervision code](https://github.com/AmirGhaffari96/aneurysm-detection-tof-mra/tree/98072ee239ef6b61b8cd2a6ab01371b3f56c446d)는
diffusion restoration, vessel pseudo-labeling, Hessian vesselness, TopCoW anatomy와
multiple-instance detection을 한 pipeline으로 결합한다. README가 결과를 보고하지만
manuscript는 in preparation이고 raw pooled imaging, finalized ethics/archive
identifier와 independent reproduction contract는 없다. 즉 이 공개 code-level
claim을 peer-reviewed truth로 높이지 않지만, diffusion+vesselness+anatomy+weak
supervision의 조합을 독립 novelty로 쓰는 것도 피한다.

## 4. nearby public assets도 학습 cohort를 만들지 않는다

[Pre/post stent-assisted-coiling record](https://zenodo.org/records/18944596)는
CC BY 4.0으로 한 paraophthalmic ICA case의 PRE/POST 3D-DSA DICOM
(194,755,060 bytes)과 두 geometry set(3,205,118 bytes)을 공개한다. Paired
intervention illustration으로는 유용하지만 독립 unit은 한 명이고 release에는 CFD
field output이 없다. Future admitted treatment task의 qualitative figure가 될 수는
있어도 development, ablation이나 outer confirmation cohort는 아니다.

[CoW GWAS summary-statistics record](https://zenodo.org/records/15084068)는
46 file/9,016,438,620 bytes의 open summary statistics를 제공한다. 이는 genotype-
phenotype association 자산이지 casewise CTA/MRA, aneurysm label, patient split 또는
same-patient imaging-genetics bridge가 아니다. Summary statistics를 image model에
붙이는 것은 correspondence를 만들어내는 것이므로 제외한다.

## 5. 비보상식 six-way screen

축은 clinical importance, target identifiability, residual novelty, asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence, ISBI schedule fit 순서다. 총점 32/40과 함께 target 3.5,
novelty 2.5, asset 3.0, unit 3.0, baseline 3.0을 각각 넘어야 한다.

| 후보 | 8축 점수 | 합계 | 판정 |
|---|---|---:|---|
| DINO-feature 3DRA segmentation extension | 4.0/4.0/0.5/2.5/2.5/5.0/4.5/3.5 | **26.5** | method가 direct code prior, training/fold/result contract 없음 |
| geometry-splatting CTA segmentation extension | 4.0/4.0/0.5/2.5/2.0/5.0/5.0/3.5 | **26.5** | geometry-to-voxel fusion direct prior, clinical unit unresolved |
| modality-agnostic anatomy-aware weak supervision | 4.5/3.5/0.5/2.0/2.5/5.0/4.5/3.5 | **26.0** | nnU-Net/prior/pseudo-label combination already publicly claimed |
| pre/post stent hemodynamic-remodeling learning | 4.0/3.5/1.0/3.5/0.5/4.5/5.0/3.5 | **25.5** | one patient, released CFD field/confirmation unit 0 |
| patient-grouped ADAM patch benchmark repair | 4.0/4.0/0.5/1.0/1.0/5.0/4.0/3.5 | **23.0** | provenance repair이지 paper identity가 아니며 lawful payload contract 없음 |
| paired ADAM change-consistency segmentation | 4.5/2.5/1.0/1.0/1.5/5.0/4.5/3.0 | **23.0** | growth/intervention target 없음, current folds는 base-ID overlap |

새 release가 크다는 사실이 novelty와 independent-unit floor를 보상하지 않는다.
어떤 row도 E0를 통과하지 않으며 score repair를 허용하지 않는다.

## 6. 운영 결론과 재진입 조건

- current schema와 primary batch: 10.7, unchanged
- current architecture: `null`; active GNN/U-Net/foundation model 0
- ADAM patch release: payload 0, acquisition 0, P0 0
- source-watch v18: 31 exact public state, review-only
- scientific server query/transfer/PBS/GPU/monitoring: 0
- historical `115645`: immutable no-verdict, repair/rerun 0
- manuscript title/abstract/method/result/table/figure/claim: 변경 없음
- future authorized execution: `introai9` PBS only, login-node GPU 금지
- `junjinyong`: 접속·조회·전송·제출·모니터링 금지

ADAM 계열 재진입에는 upstream reuse/redistribution 권한, source-image lineage,
negative control을 포함한 immutable manifest, B/F subject grouping, validation-only
selection과 untouched patient-disjoint confirmation이 필요하다. 이 조건이 충족돼도
benchmark repair만으로는 method novelty가 생기지 않는다. 별도의 clinically
identified estimand와 non-compositional failure mechanism이 noncompensatory gate를
통과해야 method-free P0를 새로 등록할 수 있다.
