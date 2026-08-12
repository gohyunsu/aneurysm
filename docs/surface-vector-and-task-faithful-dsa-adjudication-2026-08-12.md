# Surface-vector 가설과 task-faithful DSA 대안의 재판정

> **판정 · 2026-08-12:** 전달된 분석의 과학적 문제의식과 검증 순서는
> 채택한다. 그러나 새 자산 신호 없이 `fresh version`이라는 이름으로 같은
> surface-vector contract를 다시 여는 것은 local repair loop다. 제안된
> edge-1-form/Hodge/SE(3)/periodic stack은 여전히 **선택되지 않은 control
> family**이며 architecture나 novelty가 아니다. 최신 sparse-DSA 합성,
> DSA aneurysm segmentation·정량 biomarker와 synthetic-reader-study source를
> 함께 심사해도 실행 가능한 독립 주제는 나오지 않았다. 여섯 대안은
> **26.5/26.5/26.0/25.5/24.5/23.5**로 모두 기각한다. E0/P0/P1, method,
> architecture, scientific-server query, PBS/GPU, outer test와 paper claim은 0이다.

## 1. 전달된 분석에서 타당한 부분

다음 네 가지는 그대로 보존할 가치가 있다.

1. 평균 Cartesian field error가 작다고 tangent WSS의 robust zero, signed index와
   cardiac-cycle track이 보존되는 것은 아니다. 이는 반증 가능한 평가 가설이다.
2. task stability → field-error-matched failure → bounded development → fresh
   confirmation → external interpretation의 순서는 architecture-first 개발보다
   과학적으로 타당하다.
3. `115645.ECE-util1`은 running이 아니다. exact history는 `E`/exit 2,
   walltime `00:27:02`, GPU 0, aggregate/raw PBS log/persistent cache 0,
   scientific check 0/10이며 결론은 `execution-incomplete / no scientific
   verdict`다. Historical source score 32.0/40과 함께 보존하고 같은 contract를
   수리하거나 다시 실행하지 않는다.
4. GNN, edge 1-form, Hodge decomposition, equivariance, periodic operator와
   topology loss를 결합하거나 새 이름을 붙이는 것은 contribution이 아니다.

제안한 application identity도 **조건부 문장**으로는 적절하다.

> Field-accurate transient WSS surrogates may fail to preserve robust
> critical-flow organization on aneurysm surfaces.

하지만 아직 failure가 관측되지 않았으므로 `can destroy`처럼 결과를 단정하지
않는다. 같은 이유로 “structure-faithful operator가 개선한다”는 문장도 현재의
abstract claim이 아니라 E2 이후에만 쓸 수 있는 confirmatory hypothesis다.

## 2. architecture 제안에서 수정해야 하는 부분

제안된 stack은 원인과 표현을 분리해 비교할 **좋은 실험 격자**다. 그러나 한 번에
전부 넣으면 어느 요소가 실패를 해결했는지 식별할 수 없다.

| 요소 | 현재 역할 | 과도한 해석을 막는 경계 |
|---|---|---|
| vertex Cartesian vector | mandatory baseline | tangency projection과 같은 mesh/phase contract 필요 |
| oriented edge-integrated 1-form | representation control | orientation consistency를 주지만 critical-point 보존을 보장하지 않음 |
| SE(3)-equivariant mesh message passing | strong baseline/control | equivariance는 tangent-field topology나 temporal event fidelity가 아님 |
| discrete Hodge exact/coexact/harmonic split | diagnostic/control | component error가 작아도 zero pair의 birth/death는 달라질 수 있음 |
| periodic temporal operator | temporal control | 80 phase의 index가 physical phase alignment를 자동으로 보장하지 않음 |
| deterministic zero/index/track extractor | evaluation instrument | mesh·tolerance·matching rule 안정성 전에는 training target이 아님 |

특히 signed critical-point, trajectory와 birth/death loss를 처음부터 학습에 넣는
것은 부적절하다. 이 endpoint들은 mesh perturbation과 근접한 zero-pair에 대해
불연속일 수 있고, extractor의 tolerance를 모델이 공략할 수 있다. E1에서
method-free stability를 먼저 통과하고 E2에서 matched baseline failure가
관측된 뒤에만, validation-only bounded development에서 하나의 attribution
hypothesis와 연결된 최소 structural regularizer를 검토한다. 먼저 보고할
topological endpoint는 boundary margin이 확보된 region의 **signed total degree와
abstention**이며, exact point/type/worldline은 그보다 강한 후속 endpoint다.

## 3. material evidence 없이는 fresh version이 아니다

새 evidence version은 version number, wrapper, downloader, parser, timeout,
cache, seed 또는 locally generated field로 만들 수 없다. 재진입 전 최소한 다음
중 하나의 whitelisted material signal이 필요하다.

- licensed phase-resolved tangent-vector cohort와 units/mesh/BC/solver schema
- patient 또는 generating-family 단위 immutable manifest와 held-out split
- executable Cartesian/tangent/equivariant/Hodge matched baseline contract
- paired physical measurement 또는 독립 clinical/CFD reference

그 뒤에도 E0 source admission은 model이나 GPU를 허용하지 않는다. E1은
remesh/tolerance/perturbation stability, E2는 field-error-matched structural
failure, E3는 family-disjoint bounded development, E4는 fresh confirmation,
E5는 같은 좌표계·색상 범위의 external interpretation 순서다. 파열 위험이나
치료 유용성은 같은 patient-level outcome join이 없으면 주장하지 않는다.

## 4. 대체 방향으로 본 task-faithful sparse DSA

Surface-vector를 닫았다고 가까운 DSA 생성 문제를 자동 선택해서는 안 된다.
최신 직접 선행은 오히려 단순한 결합 novelty를 크게 줄인다.

### SAVE-Net: sparse acquisition과 frame synthesis를 이미 직접 점유

[SAVE-Net](https://doi.org/10.3389/fmed.2026.1793962)은 한 병원의
17,335 sequence/15,286 patient를 개발·내부평가에, 두 외부 병원의 3,255
sequence를 외부평가에 사용한다. 2D/3D, aneurysm, stenosis, AVM/AVF와
moyamoya를 포함하고, 한 real frame 뒤의 intermediate frame을 합성한다. Source는
6-frame generation, 1/7 standard dose, SSIM/PSNR, time-intensity curve,
guidewire displacement와 5-reader/200-pair 평가를 보고한다. 이 숫자는 AURORA가
재현한 결과가 아니다.

중요한 빈틈도 source가 명시한다. Formal diagnostic-consistency metric은
prospectively 정의되지 않았고, generated sequence를 이용한 IA segmentation이나
CVS detection 같은 real-world downstream task는 평가하지 않았다. 그러나 이는
곧바로 AURORA novelty가 아니다. Sparse synthesis, dose framing, temporal curve,
reader confidence와 disease-exclusion OOD는 이미 원 연구의 직접 범위이며,
data는 corresponding author에게 reasonable request 조건이다. 공개 versioned
patient/sequence/exposure/aneurysm-mask/QDSA split asset은 확인되지 않았다.

### Real-DSA segmentation에서 morphology와 QDSA까지 이미 평가

[dual-centre TransUNet study](https://doi.org/10.1016/j.ejrad.2026.112882)는
1,539 patient의 2,777 DSA image를 이용해 UNet, VNet, DeepLabV3, SwinUNet와
TransUNet을 비교한다. Official indexed metadata는 1,212 internal patient/
2,219 image와 327 external patient/558 image, segmentation뿐 아니라 aneurysm
morphology와 CBF/CBV/MTT/TTP agreement를 보고한다. Source-reported Dice와 ICC는
AURORA result가 아니다. Multiple, fusiform/dissecting lesion과 poor-quality
image를 제외한 single-saccular 범위이며, inspected source에서 versioned public
patient/image/mask/QDSA/split/code asset은 확인되지 않았다.

따라서 “SAVE-Net-generated DSA에 segmentation을 적용해 morphology/QDSA를
보존한다”는 질문은 임상적으로 중요하지만, 두 직접 선행의 가장 가까운 미평가
cell을 결합한 것이다. 독립적인 failure mechanism, 공개 paired target과
non-compositional algorithmic gap이 없으면 contribution이 아니다.

### Synthetic DSA reader-study release도 현재 task asset이 아님

[arXiv:2602.11703](https://arxiv.org/abs/2602.11703)은 single-centre 99,349
frame으로 semantically conditioned latent diffusion model을 학습하고, 네 명의
expert가 400 synthetic image를 평가했다고 보고한다. Source-reported Likert,
ICC와 FID는 AURORA result가 아니다.

[Zenodo 21104782 revision 4](https://zenodo.org/records/21104782)는 CC BY 4.0으로
표시되지만 2026-10-31까지 embargoed다. Metadata는 anterior/posterior circulation,
four C-arm views의 400 synthetic PNG만 설명하며 original patient DSA가 없다고
명시한다. Public patient pair, aneurysm mask, lesion identity, frame sequence,
exposure, morphology/QDSA reference와 downstream label은 0이다. Embargo 해제는
fresh source re-audit 신호일 뿐 E0/P0, method나 compute 권한이 아니다.

### DIAS는 공개지만 필요한 endpoint가 다름

[DIAS v3](https://zenodo.org/records/11637181)는 60 patient/120 sequence와
60 fully annotated sequence의 merged 2D vessel mask를 공개한다. 그러나 release는
원 6--46 frame에서 expert가 arterial phase 4--14 frame을 미리 골라 만든 것이고,
framewise arrival truth, exposure/timestamp, aneurysm mask, QDSA biomarker,
prospective stop action과 treatment outcome을 제공하지 않는다. Public asset은
baseline 교육에는 유용하지만 SAVE-Net의 low-dose acquisition이나 TransUNet의
aneurysm biomarker preservation을 검증하는 reference가 아니다.

## 5. 비보상식 six-way delta screen

축은 clinical importance, target identifiability, residual novelty, asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence, ISBI schedule fit 순서다. 총점 32/40과 함께 target 3.5,
novelty 2.5, asset 3.0, unit 3.0, baseline 3.0을 모두 넘어야 한다.

| 후보 | 8축 점수 | 합계 | 판정 |
|---|---|---:|---|
| task-faithful sparse DSA biomarker preservation | 4.5/3.0/1.0/2.0/2.5/5.0/5.0/3.5 | **26.5** | SAVE-Net+TransUNet의 obvious composition, paired public target 없음 |
| adaptive acquisition stopping with downstream risk | 5.0/2.5/1.5/2.0/2.5/5.0/5.0/3.0 | **26.5** | 실제 stop/dose/action target과 raw full-phase contract 없음 |
| post-treatment coil-robust QDSA segmentation | 4.5/3.5/0.5/1.0/3.5/5.0/5.0/3.0 | **26.0** | real-DSA segmentation→QDSA가 direct prior, public target 없음 |
| downstream segmentation transport on generated DSA | 4.5/3.5/1.0/1.0/3.0/4.5/5.0/3.0 | **25.5** | source data request-only, synthetic release embargoed·label 없음 |
| rare-pathology OOD sparse synthesis | 4.5/3.0/0.5/1.0/3.0/4.5/5.0/3.0 | **24.5** | disease-exclusion OOD가 SAVE-Net에 직접 포함됨 |
| reader-calibrated hallucination detection | 4.5/2.5/1.5/1.0/2.0/4.0/5.0/3.0 | **23.5** | casewise error/action reference와 public reader manifest 없음 |

높은 임상 중요도와 좋은 figure 가능성이 낮은 novelty나 asset을 보상하지 않는다.
현재 pose/operator primary batch와 schema 10.7은 이 delta로 바꾸지 않는다.

## 6. 운영 결론

- surface-vector: `closed_until_whitelisted_material_release` 유지
- current architecture: `null`; GNN 기반 active model 0
- structure extractor: evaluation-only until E1 stability
- historical `115645`: immutable no-verdict, repair/rerun 0
- DSA delta: all six rejected; payload/request/P0/method/model 0
- source-watch: synthetic DSA embargo record만 manual re-audit용으로 freeze
- scientific server query/transfer/PBS/GPU: 0
- future gate-authorized execution: `introai9` PBS only, login-node GPU 금지
- `junjinyong`: 접속·조회·전송·제출·모니터링 금지
- manuscript title/abstract/method/result/table/figure/claim: 변경 없음
