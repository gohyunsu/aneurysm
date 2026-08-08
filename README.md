# AURORA · Aneurysm Research

실패한 가설을 보존하면서 뇌동맥류 영상·혈류 연구의 문제 정의부터 다시
검증하는 공개 연구 저장소입니다. 기존 partial/missing-BC operator identity는
N1c와 후속 3D gate에서 지지되지 않았고, 현재 선택된 method는 없습니다.

새 active candidate는 **intracranial 4D-flow MRI의 protocol-indexed posterior
prediction**입니다. 한 acquisition에서 추론한 latent flow posterior가 같은
controlled phantom flow의 다른 resolution·acceleration·VENC acquisition을
measurement space에서 예측할 수 있는지를 묻습니다. Generic
super-resolution, denoising, PINN reconstruction 또는 voxelwise uncertainty를
새 contribution이라고 부르지 않습니다.

> **AURORA** — 기존 프로젝트명은 유지하지만, 새 candidate의 정식 방법명과
> architecture는 I0b/I0c 근거 전에는 정하지 않습니다.

## 현재 단계 · I0a 14/14 통과, I0b one-shot audit 등록

[`I0a contract`](configs/flow_mri_protocol_i0a_asset_audit.json)는 두 공개
paired-protocol phantom release의 공식 record, archive size/checksum, ZIP
central directory, descriptor/PAR/XML header와 payload byte contract를 14개
check로 감사합니다. 등록 전에 record·central directory·header를 발견한
사실을 명시했으며 field value, processed RAW, REC는 읽지 않았습니다.

Exact public source `f7b4e024d69d43cf042f4163342b4d993386f441`의 CPU
audit은 exit 0, **14/14 pass**였습니다. 두 archive의 250개 central-directory
entry, descriptor 9개, primary header 8개를 CRC와 함께 검증했고 processed
RAW/REC payload read는 0입니다. 공개 aggregate는
[`I0a result`](results/flow_mri_protocol_i0a_asset_audit_20260808.json)입니다.

이 범위에서
[`I0b contract`](configs/flow_mri_protocol_i0b_task_adequacy.json)를 field read
전에 고정했습니다. I0b는 2021 processed RAW 27개만 selective staging해
3×3 protocol의 alignment·field discrepancy·temporal correlation을 측정합니다.
동시에 새 [33-scan intervention release](https://doi.org/10.5281/zenodo.17183575)의
세 ZIP64 central directory와 33개 primary PAR header에서 5 base geometry,
22 model/device state, 8 multi-VENC state, 2 pump-off scan과 15 device condition을
감사합니다. 이 discovery는 등록 전에 수행했음을 명시하며 REC는 읽지 않습니다.

33 scans는 33 patients가 아닙니다. Base geometry는 5개이고 source patient
anatomy는 2개뿐이며 exact-protocol repeat도 없습니다. I0b가 모두 통과해도
method-free PAR/REC decoder·noise audit인 I0c 등록만 열립니다. Method, posterior
calibration claim, neural/GPU training, outer test와 ISBI submission은 아직
열리지 않습니다.

## 보존된 이전 연구선과 제출 상태

제출 목표는 **IEEE ISBI 2027 four-page regular paper**입니다
(공식 마감 2026-10-26). 다만 N1c와 V1 3D backbone gate에 이어 V1e
known-condition qualification도 6/9로 실패했습니다. V1b/V1c/V1d의 boundary
asset·geometry 통과와 V1e의 상대 boundary utility는 model learnability나
method evidence가 아닙니다. Current Aneumo 3D learning line을 중단했으므로
submission-ready가 아닙니다. ISBI에 맞춘 좁은 claim,
velocity-only 3D 실험, five-seed outer-test와 kill date는
[`docs/isbi-2027-plan.md`](docs/isbi-2027-plan.md)에 고정합니다.

[`ISBI V0 contract`](configs/aneumo_isbi_v0.json)는 exact source `0589070`에서
8/8 check를 통과했습니다. 모델을 학습하거나 새 field array를 읽지 않고,
64-case compact cache의 checksum·family split·scalar inflow design law와
기존 train-only scaling evidence만 감사했습니다. 이 결과는
[`public aggregate`](results/aneumo_isbi_v0_20260808.json)에 있으며 V1 구현
smoke만 엽니다. Headline, outer test와 submission은 열리지 않습니다.

결과 전에 고정한
[`V1 backbone smoke`](configs/aneumo_isbi_v1.json)는 동일한
train/validation family와 1,024-node development subset에서 q-PointNet,
kNN-MGN, DeltaPhi graph residual, frame-free anchor-token equivariant
operator를 세 seed로 비교합니다. Candidate라는 이름에 우선권을 주지 않고
response L2 → full-q L2 → exact missing energy 순으로 backbone만 고릅니다.
세 seed의 matching-q 평균과 seed×8 q의 24-component missing mixture는
분리해 집계하고, same-case scaling은 true validation anchor를 쓰는
response-only oracle라 선택에 사용하지 않았습니다. Test field와 outer-test
권한을 닫은 채 12/12 task를 완료했지만 gate는 5/7로 실패했습니다. 선택
q-PointNet의 worst-seed full-q/response L2가 `1.03459/1.00354`로 기준
`0.35/0.50`을 크게 넘었습니다. Public aggregate는
[`results/aneumo_isbi_v1_20260808.json`](results/aneumo_isbi_v1_20260808.json)입니다.
현재 backbone branch는 local tuning 없이 중단했습니다. 이어진
[`V1a fixed-checkpoint attribution`](results/aneumo_isbi_v1_attribution_20260808.json)은
네 family의 train full-q L2도 `0.769--0.956`으로 높고 출력 norm과 방향
정렬이 함께 약함을 확인했습니다. 따라서 실패는 새로운 geometry에만 생긴
일반화 문제가 아니라 training fit부터 나타난 task/representation
부적합입니다. Condition variation 자체는 validation field energy의 약
15.7%로 비자명하지만, 이 결과는 새 model이나 V2를 열지 않습니다. 다음은
geometry-only reconstruction을 수선하는 대신 새 task/data identity가
식별 가능하고 충분히 비자명한지를 별도 감사하는 단계입니다.

중요한 asset 정정도 있습니다. Boundary marker와 surface mesh가 없는 것은
기존 compact cache이지 공식 Aneumo release 전체가 아닙니다. Pinned ZIP64의
archive 1/case 1에서 `.msh`, `.stl`, volume `.vtu`, `inlet/outlet/wall.vtp`,
connectivity와 `U/p` array를 확인했습니다. 이 사전 발견을 결과처럼 과장하지
않고 [`V1b boundary-asset audit`](configs/aneumo_isbi_v1b_boundary_asset_audit.json)에
명시했습니다. Exact source `fb1c21a`의 V1b는 20 archives·64 cases, 384
required member와 train representative 60 VTP를 감사해 8/8을 통과했습니다.
공개 결과는
[`V1b aggregate`](results/aneumo_isbi_v1b_boundary_asset_audit_20260808.json)입니다.
Validation/test payload와 field array는 읽지 않았습니다.

이 통과가 허용한 다음 단계는 모델이 아니라
[`V1c train-only boundary-geometry audit`](results/aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json)이었습니다.
Exact source `84fc244`에서 20 train-family representative의 세 patch×세 flow,
180 payload를 감사해 8/8을 통과했습니다. 60/60 patch geometry가 flow에 따라
정확히 같았고 minimum polygon-valid fraction은 1.0이었습니다.
`U/p/TimeValue`, validation/test, checkpoint와 학습은 읽지 않았습니다.

이 결과가 연 것은 다시 모델이 아니라
[`V1d development geometry-cache audit`](results/aneumo_isbi_v1d_development_geometry_cache_20260808.json)이었습니다.
Exact source `369317a`에서 train 40·validation 12·test 0 case의 boundary
468개와 reference-volume 52개 payload를 geometry-only로 감사해 9/9을
통과했습니다. 156/156 patch가 q-invariant였고, 52/52 case에서 모든 boundary
point가 reference-volume point에 exact하게 대응했으며 minimum polygon-valid
fraction은 1.0이었습니다. 이는 model evidence가 아닙니다.

V1d가 허용한 범위에서 어떤 학습보다 먼저
[`V1e known-condition baseline`](configs/aneumo_isbi_v1e_known_condition_baseline.json)을
고정했습니다. Exact source `c62838b`에서 동일 parameter·320 source-token
budget의 boundary Perceiver와 geometry-only control을 fresh three-seed로
비교했고 6 GPU task가 모두 정상 완료됐습니다. Boundary는 두 primary metric에서
3/3 seed로 control보다 좋았고 seed-mean 상대 개선도 full `10.94%`, response
`6.41%`였습니다. 그러나 worst-seed train/validation full-q와 response L2가
`0.77221/0.87796/0.94918`로 기준 `0.25/0.35/0.50`을 모두 넘어서 frozen
gate는 [`6/9 fail`](results/aneumo_isbi_v1e_known_condition_baseline_20260808.json)입니다.
Boundary asset이 geometry-only보다 유용하다는 engineering signal은 있지만,
known-condition learnability도 partial/missing method도 입증되지 않았습니다.
등록대로 architecture·loss·step·seed·threshold를 국소 수정하지 않고 current
Aneumo 3D learning line을 중단합니다. Scalar missing-inflow protocol, test/V2,
novelty와 submission은 열리지 않습니다.

## 현재 모델은 GNN인가?

**현재 실행된 exact/nonlinear 모델은 GNN이 아닙니다.** Context MLP와
boundary token, lifted spatial decoder로 method gate를 검사했습니다.
V1에는 q-PointNet, kNN-MGN, DeltaPhi graph와 frame-free anchor-token
candidate가 실제 학습됐지만 네 family 모두 relative L2 약 1로 실패했습니다. 그보다 큰
edge-message GNN + anatomy token + continuous-query decoder는 Aneumo
irregular-3D용 장기 **target specification**입니다. 따라서 어느 쪽도
사이트와 논문에서 검증된 “현재 모델” 또는 확정 contribution이라고 부르지
않습니다.

의학·CFD·mesh·GNN 배경이 없는 독자는
[`site/learn.html`](site/learn.html)에서 11개 장을 순서대로 읽을 수 있습니다.

## 왜 방향을 바꿨는가

기존의 autoregressive MeshGraphNet 개선안은 현재 velocity와 inlet context를
필요로 합니다. 따라서 geometry-only AneuX에 그대로 적용할 수 없고, 2026년
선행연구가 이미 inflow-aware GNN, graph transformer, masked pretraining,
multigrid, physics-informed loss를 폭넓게 다룹니다. attention이나 masking을
추가하는 것만으로는 연구 gap도, 임상적 타당성도 충분하지 않습니다.

AURORA는 다음 세 질문을 한 모델과 실험 프로토콜로 연결합니다.

1. 관측된 BC component가 달라도 예측들이 하나의 확률법칙의
   조건부·주변 분포로 일관되는가?
2. 그 구조적 일관성이 independent conditionals보다 낮은 conditional
   accuracy라는 대가 없이 가능한가?
3. 그 차이가 solution-functional Bayes action과 다음 BC 측정 선택의
   실제 regret를 줄이는가?

현재 답은 “아직 아니다”입니다. N1c-a는 joint density/objective가
주 병목이고 operator는 부차적임을 보였으며, route compatibility는
달성했지만 robust decision superiority는 확인하지 못했습니다. Paired
response supervision은 독립 contribution이 아니라 ablation으로 내렸고
uncertainty separation은 아직 secondary hypothesis입니다.

다음 두 작업은 결과를 보기 전에 별도 config로 고정한 뒤 완료했습니다.
[`density-objective audit`](configs/nonlinear_pde_n1_density_objective_audit.json)은
동일 joint 2-GMM에서 네 training objective만 validation-only로 비교하고,
[`decision-task audit`](configs/nonlinear_pde_n1_decision_task_audit.json)은
learned model 없이 true law와 true simulator만으로 acquisition task의
비자명성과 Monte Carlo 안정성을 측정했습니다. Full-joint objective는
N1c raw 대비 세 mask의 exact-law excess를 20.3–27.2% 줄였고 모두 5/5
seed 방향이 같았습니다. Missing task는 안정적인 nonzero VoI를 보였지만,
sparse-2는 96/96 context에서 같은 component가 winner여서 adaptive-policy
비교에는 부적합했습니다. 두 결과 모두 method를 선택하거나 N1c·3D 상태를
바꾸지 않습니다.

그 다음 단일 mechanism falsification은 결과 전에
[`M0 contract`](configs/nonlinear_pde_n1_missing_operator_pullback_m0.json)로
고정했습니다. Missing mask에서 각 후보 BC component와 solution
functional의 joint pushforward를 frozen operator를 통해 점수화합니다.
Full-joint MLE, generic boundary-kernel, solution-marginal proper-score를
같은 초기화·minibatch·난수로 비교하고, 세 fresh development seed의
candidate-joint MMD²와 true-oracle acquisition regret가 모두 5% 이상
개선되어야 합니다. Density·solution marginal·operator 정확도 보호 조건도
전부 통과해야 합니다. 하나라도 실패하면 hyperparameter를 국소 조정하지
않고 mechanism을 폐기합니다. 통과해도 별도 fresh re-entry 설계 자격일
뿐 method selection, novelty, N1c relabel 또는 3D 권한이 아닙니다.

Exact `89bdc85`의 M0 실행은 seed 0/2만 완료되고 seed 1이 truncated
conditional rejection에서 중단되었습니다. 등록된 3-seed aggregate를 만들
수 없어 pass/fail이 아닌 `execution-incomplete / no scientific verdict`로
기록했습니다. 성공 seed metric은 선택적으로 집계하지 않았고 sampler
repair·rerun·fresh re-entry도 열지 않았습니다. 공개 execution record는
[`results/nonlinear_pde_n1_missing_operator_pullback_m0_execution_20260808.json`](results/nonlinear_pde_n1_missing_operator_pullback_m0_execution_20260808.json)입니다.

Fixed Fourier cycle은 frozen D0의 localized bulge gate를 실패해 제거했습니다.
D0b에서는 DCT-II 17/25가 탈락하고 train-only POD 17/25만 oracle
representation gate를 통과했습니다. POD는 아직 learned superiority나
선택된 architecture가 아니며, compute-matched 비교와 fresh transient
확인을 통과할 때만 one-shot temporal branch를 다시 검토합니다.

## 문서 읽는 순서

1. [`docs/research-direction.md`](docs/research-direction.md) — 연구 질문,
   contribution, novelty, kill criteria
2. [`docs/literature-lineage.md`](docs/literature-lineage.md) — 선행연구 계보와
   직접 경쟁작 비교
3. [`docs/model-spec.md`](docs/model-spec.md) — AURORA 입력·모듈·loss·tensor
   계약
4. [`docs/experiment-protocol.md`](docs/experiment-protocol.md) — 데이터 역할,
   nested evaluation, ablation, 통계
5. [`docs/isbi-2027-plan.md`](docs/isbi-2027-plan.md) — ISBI 4-page claim,
   3D experiment gate, calendar
6. [`CHANGELOG.md`](CHANGELOG.md) — 결정과 구현 변경 이력
7. [`site/index.html`](site/index.html) — 연구 판단을 압축한 프로젝트 허브
8. [`site/learn.html`](site/learn.html) — 동맥류·CFD·GNN·operator·실험을
   처음부터 설명하는 상세 field guide
9. [`docs/server-execution.md`](docs/server-execution.md) — 비식별 자산 감사와
   scheduler 실행 provenance

기존 데이터 감사 기록은 [`docs/datasets.md`](docs/datasets.md)와
[`docs/reproduction.md`](docs/reproduction.md)에 보존합니다.

## 실행 가능한 연구 계약

```bash
PYTHONPATH=src python -m aurora.protocol validate configs/aurora_v1.json
python -m unittest discover -s tests -v
```

설정 파일은 task 정의, split 단위, gate, loss, provenance를 함께
검증합니다. 연구 방향이 바뀌면 문서만 수정하지 말고 이 계약과 사이트의
변경 이력도 같은 커밋에서 갱신합니다.

CMHA legacy exploratory diagnostic은 scheduler allocation과 pinned container에서
실행합니다. 공개 template은 `cluster/`, 실행 코드는
`experiments/run_cmha_g1.py`에 있으며, source identifier는 run artifact에
기록하지 않습니다.

2026-08-03 표 기반 exploratory 결과는 real-CFD summary의 incremental
rupture-status utility를 지지하지 않았습니다(`ΔAUPRC=-0.0419`,
patient-bootstrap 95% CI `[-0.1083, 0.0066]`). 이 결과 때문에 downstream
risk alignment는 논문의 primary contribution에서 제외했습니다.

현재 Aneumo ZIP64 release는 전체 archive를 내려받지 않고 byte-range로
감사했습니다. 첫 shard에서 geometry당 8개 steady mass-flow condition과
실제 internal NPY의 좌표·압력·속도·CRC contract를 확인했고, 32개 AneuX
base family × 2 deformation의 family-disjoint selective pilot을 결과 확인
전에 등록했습니다. 이후 512 member를 selective range-read해 64 case,
case당 8 condition과 4,096 node의 compact cache를 완성했고, 40/12/12
case family-disjoint split과 finite field를 검증했습니다. Compact cache는
dataset license에 따라 공개 재배포하지 않습니다. BenchAnXplore 105-case
HDF5/XDMF archive는 무결성을 확인해 결과 확인 전에 D0를 등록하고
실행했습니다.
Fixed Fourier는 실패했으며, 후속 D0b도 표현 가능성만 판단할 뿐 모델 성능
또는 novelty로 해석하지 않습니다. Main method는 exact controlled PDE →
nonlinear PDE → paired-BC irregular 3D 순서로 검증합니다.

D0 첫 실행은 scheduler walltime으로 종료되어 metric이 없었습니다.
동일 protocol의 attempt 2는 정상 완료됐지만 frozen \(K=8\) gate를
실패했습니다. \(K=12\)도 bulge relative L2 기준을 통과하지 못해 fixed
Fourier decoder는 중단합니다. 두 provenance는
[`results/benchanxplore_d0_attempt1_20260803.json`](results/benchanxplore_d0_attempt1_20260803.json)에
와
[`results/benchanxplore_d0_attempt2_20260803.json`](results/benchanxplore_d0_attempt2_20260803.json)에
남겼습니다.

첫 method sanity experiment는
[`configs/controlled_pde_g1.json`](configs/controlled_pde_g1.json)에 5개
seed, mask, metric, threshold를 결과 전에 고정했습니다. Exact Poisson
family에서 learned joint BC density + shared operator를 direct masked
Gaussian baseline과 비교합니다. PBS 실행 코드는
[`cluster/ssu_a6gpu_controlled_g1.pbs`](cluster/ssu_a6gpu_controlled_g1.pbs)이며,
통과해도 pipeline sanity일 뿐 novelty 성능으로 해석하지 않습니다.
Frozen 5-seed run은 absolute mean, coverage, raw projective gate를 모두
통과하지 못했습니다. Direct baseline보다 일관된 상대 개선은 있었지만
claim은 `unsupported`이며 결과는
[`results/controlled_pde_g1_attempt2_20260803.json`](results/controlled_pde_g1_attempt2_20260803.json)에
있습니다. G1b는 finite-sample metric floor와 density/operator/MC error를
분해하는 exploratory diagnostic으로 완료됐습니다. K=128 raw projective
distance는 iid floor로 설명됐지만, K=2048 missing-mask mean error가
0.0853이고 density estimation error가 지배적이어서 기존 G1 실패는 그대로
유지합니다. 공개 aggregate는
[`results/controlled_pde_g1b_20260803.json`](results/controlled_pde_g1b_20260803.json)입니다.

후속 [`G1r`](configs/controlled_pde_g1r.json)은 기존 G1을 다시 채점하지
않습니다. G1b가 드러낸 density optimization과 estimator-floor 문제만
수정하고, 서로 겹치지 않는 5개 fresh seed를 결과 전에 고정했습니다.
Density와 operator는 validation geometry로만 checkpoint를 선택하고,
density-only moment·coverage는 analytic하게, end-to-end mean은
Gauss–Hermite quadrature로, projective error는 matched iid floor 대비
95% CI upper bound로 평가했습니다. Exact commit `951ace1`의 prospective
run은 정상 완료됐지만 실패했습니다. Coverage, full-BC operator, analytic
nesting, projective-excess는 통과한 반면, 최악 seed의 density-only mean
0.07533과 end-to-end quadrature mean 0.07518이 고정 기준 0.05를
넘었습니다. 다섯 seed 평균이 기준 아래라는 이유로 gate를 완화하지 않으며,
공개 aggregate는
[`results/controlled_pde_g1r_20260803.json`](results/controlled_pde_g1r_20260803.json)에
있습니다. Density estimation의 representation·optimization·finite-data
오차를 분해하기 전까지 nonlinear/3D confirmatory 학습은 보류합니다.

Post-G1r density attribution은
[`configs/controlled_pde_density_attribution.json`](configs/controlled_pde_density_attribution.json)에
별도로 고정해 완료했습니다. Analytic population NLL은 최악 density-only
error 0.00495를 회복했지만 empirical NLL은 0.04401–0.04855였습니다.
동일 6,144 boundary sample의 192×32, 768×8, 3,072×2와 fixed-axis 비교는
geometry coverage와 repeated-condition information이 모두 필요함을
보였습니다. 이는 threshold가 없는 post-result attribution이며 실패한
G1/G1r을 relabel하지 않습니다. 공개 aggregate는
[`results/controlled_pde_density_attribution_20260803.json`](results/controlled_pde_density_attribution_20260803.json)에
있습니다.

후속 DA2는
[`configs/controlled_pde_density_development.json`](configs/controlled_pde_density_development.json)에
development-only로 등록했습니다. 세 새 seed에서 empirical NLL과 grouped
unbiased/shrinkage estimator를 같은 network·optimizer로 비교하며,
원래 G1r과 같은 768×8에서 후보를 선택합니다. 3,072×8은 데이터 증가
효과만 보는 control입니다. 결과에는 pass threshold가 없고,
선택된 estimator도 별도 fresh exact gate 전에는 nonlinear/3D 학습을
허용하지 않습니다.

DA2도 완료됐습니다. 고정 규칙상 shrinkage 0.50이 선택됐지만 원래
768×8 empirical NLL 대비 평균 개선은 0.23%에 불과하고 한 seed에서는
악화돼 material한 estimator 이득으로 보지 않습니다. 반면 3,072×8의
기존 empirical NLL은 평균 0.02575, 최악 0.02706으로 안정화됐습니다.
공개 aggregate는
[`results/controlled_pde_density_development_20260803.json`](results/controlled_pde_density_development_20260803.json)이며,
다음 fresh gate는 새 방법이 아니라 데이터 충분성을 검증합니다.

그 fresh gate는
[`configs/controlled_pde_g1s.json`](configs/controlled_pde_g1s.json)에
실행 전에 고정했습니다. 이전 실험과 겹치지 않는 5개 seed에서 original
empirical NLL, 3,072 geometry × 8 condition을 사용하고 G1r의 model,
optimizer, validation/test size, metric, threshold를 그대로 유지합니다.
Checkpoint 선택 뒤 기존과 같은 192-geometry fresh test를 생성합니다.
G1s는 exact commit `b0e555a`의 fresh 5-seed A6000 run에서 모든 frozen
check를 통과했습니다. 최악 density-only/end-to-end mean은
0.02863/0.02977, coverage error는 0.00836/0.01294, projective CI upper는
0.000674였습니다. 공개 aggregate는
[`results/controlled_pde_g1s_20260803.json`](results/controlled_pde_g1s_20260803.json)입니다.
이 결과는 nonlinear/3D protocol 등록을 허용하지만 data/pipeline sanity이지
논문의 독립 novelty가 아닙니다. G1/G1r 실패는 그대로 보존합니다.

다음 단계는 학습이 아니라 nonlinear gate 실패 원인 분해입니다.
[`configs/nonlinear_pde_n0.json`](configs/nonlinear_pde_n0.json)의 N0는
33/65 nested grid semilinear PDE, 8-component edge BC,
context-conditioned 2-GMM에서 solver accuracy, nonlinear departure, 모든
BC 방향의 response, functional diversity와 analytic conditioning route를
판정했습니다. Exact `0ead687`의 3-seed run은 9개 중 8개를 통과했지만
worst-seed nonlinear departure 0.00727이 frozen 0.01 기준을 넘지 못해
실패했습니다. 공개 aggregate는
[`results/nonlinear_pde_n0_20260803.json`](results/nonlinear_pde_n0_20260803.json)입니다.

연속 slice 때문에 nonlinear reference 12개가 단일 context에 몰렸다는
사후 진단이 있으나 N0를 합격으로 바꾸지 않습니다. Threshold 없는
[`N0a all-context attribution`](configs/nonlinear_pde_n0_attribution.json)은
기존 세 seed의 24×12 전체 격자에서 이 가설만 검사하며 성공 기준이나
실행 권한이 없습니다. Exact `749f596` 결과에서 failed seed의
contiguous/stratified/all-case median은 0.00774/0.01221/0.01828이었습니다.
이는 slice 편향 가설을 지지하지만 context median이 former 0.01 이상인
비율은 18–19/24라 uniformly nonlinear하다고 주장하지 않습니다. 공개
aggregate는
[`results/nonlinear_pde_n0_attribution_20260803.json`](results/nonlinear_pde_n0_attribution_20260803.json)입니다.
그 뒤 새로운 seed와 24-context-stratified sampling을
동결한 [`N0r`](configs/nonlinear_pde_n0r.json)는 exact `37d31a8`
A6000 run에서 9/9 check를 통과했습니다. 최악 seed nonlinear departure는
0.01933, grid error는 0.00375, 8-component response minimum은
0.17484였습니다. 공개 aggregate는
[`results/nonlinear_pde_n0r_20260805.json`](results/nonlinear_pde_n0r_20260805.json)입니다.
이제 LANO/NOP/generic probabilistic operator, ACFlow/ACO와 NOTS-style
functional acquisition을 포함한
[`N1 상세 계약`](configs/nonlinear_pde_n1.json)을 결과 전에 동결했습니다.
후보 novelty는
active acquisition 자체가 아니라 conditioning-route 불일치가 PDE
solution-functional decision과 acquisition regret에 만드는 결과입니다.
N0/N0r 통과만으로 이를 contribution이라 하지 않으며 3D headline도 열지
않습니다.

N0r는 N1 상세 protocol 등록만 허용했습니다. 이후 validation-only
development와 다섯 seed의 50개 checkpoint freeze를 거쳐, exact source
`62605a0`에서 처음으로 N1c outer test를 열었습니다. A6000 run은
125/125 contract와 5 seed를 정상 완료했지만 **N1c는 failed**입니다.

- full-BC operator L2 0.01404, coverage error 0.03281, AURORA route-action
  disagreement 0은 통과했습니다.
- Missing/sparse-2 functional energy는 independent heads보다 각각
  0.65%/1.09% 나빴고 AURORA가 좋은 seed는 0/5였습니다.
- Missing acquisition regret는 ACFlow보다 2/5 seed에서만 낮았습니다.
- Pair loss는 pair-zero보다 3/5 seed에서만 좋고, 평균 paired-response도
  DeltaPhi-style residual보다 나빴습니다.

따라서 현재 방법은 AAAI-ready가 아니며 paired supervision은 독립
contribution에서 ablation으로 내렸습니다. Route VoI 보조 계산의
common-random-number 위반도 발견해 그 두 보조 지표는 제외했습니다.
이는 gate에 사용되지 않았으므로 failed 판정은 바뀌지 않습니다. 공개
aggregate는
[`results/nonlinear_pde_n1c_20260805.json`](results/nonlinear_pde_n1c_20260805.json)입니다.
후속
[`N1c-a threshold-free attribution`](configs/nonlinear_pde_n1c_attribution.json)도
exact `b97899c`의 A6000에서 완료됐습니다. Joint density conditional
excess NLL은 missing/sparse-2/partial-4 모두 independent heads보다
0/5 seed로 열세였습니다. Functional energy의 mean oracle-substitution
difference는 density가 operator보다 missing에서 13.0배, sparse-2에서
5.81배 컸습니다. Missing acquisition은 안정화된 64×128 budget에서도
ACFlow보다 1/5 seed에서만 좋았고 sparse-2는 두 learned policy가 모두
oracle과 같아 판별력이 없었습니다. AURORA route compatibility는
수치적으로 성립했지만 independent heads보다 worst-route risk가 낮은
seed는 3/5뿐입니다.

따라서 N1c failed, 3D blocked와 `not accept-ready` 판정은 유지합니다.
공개 aggregate는
[`results/nonlinear_pde_n1c_attribution_20260806.json`](results/nonlinear_pde_n1c_attribution_20260806.json)입니다.
결과 전에 고정한 validation-only
[`density-objective control`](configs/nonlinear_pde_n1_density_objective_audit.json)과
true-law/simulator-only
[`decision-task adequacy audit`](configs/nonlinear_pde_n1_decision_task_audit.json)도
exact `337c75e`의 A6000에서 완료됐습니다.
전자는 fresh 5 seed에서 N1c raw conditional, per-component normalization,
full-joint와 registered composite objective를 같은 schedule로 비교하고,
후자는 learned checkpoint를 전혀 읽지 않았습니다. Full-joint excess는
missing/sparse-2/partial-4에서 0.04622/0.05923/0.07808로 raw 대비
27.2%/23.8%/20.3% 낮았습니다. Missing acquisition의 VoI는 두 replicate
0.15587/0.15558, winner agreement는 0.9271이었습니다. Sparse-2 VoI도
양수였지만 component 6이 모든 context의 고정 winner였습니다. 공개
aggregate는
[`density result`](results/nonlinear_pde_n1_density_objective_audit_20260806.json)와
[`task result`](results/nonlinear_pde_n1_decision_task_audit_20260806.json)입니다.
둘 다 새 contribution이나 fresh gate가 아니며 N1c failed와 3D blocked를
유지합니다.

이 evidence 뒤 등록한 M0는 solution marginal score 자체를 novelty로
주장하지 않습니다. 같은 \(B_j\)와 solution marginal을 갖더라도 dependence가
다르면 post-measurement Bayes risk가 달라진다는 식별성 gap만 겨냥했습니다.
실행은 2/3 seed만 완료돼 scientific verdict가 없고 branch는 inactive이며,
selected method는 없습니다.

D0b에서 DCT-II rank 17/25는 탈락했고 train-only POD rank 17/25가 모든
frozen representation 기준을 통과했습니다. POD-17의 full L2는 0.00141,
bulge L2는 0.00880입니다. 다만 같은 105 case가 architecture discovery에
쓰였으므로 BenchAnXplore learned 비교는 exploratory이며, confirmatory
효율 주장은 fresh transient test가 필요합니다. 공개 aggregate는
[`results/benchanxplore_d0b_20260803.json`](results/benchanxplore_d0b_20260803.json)입니다.

Aneumo pilot의 고정 split과 허용 범위는
[`configs/aneumo_g2_pilot_v1.json`](configs/aneumo_g2_pilot_v1.json)에,
선택적 ZIP64 range ingestion은
[`scripts/stage_aneumo_range.py`](scripts/stage_aneumo_range.py)에 있습니다.
이 steady scalar-BC pilot은 same-geometry response C2와 irregular-3D
일반화만 검사하며, multicomponent partial-BC C1이나 transient 효율을
뒷받침하지 않습니다.

학습에 앞서
[`configs/aneumo_scaling_audit_v1.json`](configs/aneumo_scaling_audit_v1.json)
은 train base family만 읽는 비자명성 gate를 고정합니다. 같은 case의 한
anchor field까지 제공한 강한 oracle에 대해 velocity-linear,
gauge-invariant pressure-quadratic scaling과 train-tuned global power
law를 검사합니다. Tuned scaling이 response norm의 15%도 남기지 않으면
해당 채널은 G2 novelty 근거에서 제외하며, 두 채널 모두 실패하면 Aneumo
학습을 중단합니다. 이는 단순 물리 스케일링을 새 방법의 성과로 오인하지
않기 위한 사전 감사입니다.

Exact commit `e12ff0a`의 train-only 감사 결과, velocity는 tuned
\(Q^{1.075}\) scaling 뒤에도 response residual median 0.2112,
base-family bootstrap 95% CI `[0.2001, 0.2243]`로 기준을 통과했습니다.
Pressure는 tuned \(Q^{1.75}\)에서 0.1369 `[0.1190, 0.1496]`로
실패했습니다. 따라서 미래 Aneumo G2는 velocity-only 후보이며
pressure/full-field novelty는 제외합니다. 이 결과는 learned 성능이 아니고
G1s pass 뒤 protocol 등록은 가능하지만 nonlinear N0/N1 strong-baseline
검증을 먼저 수행하므로 3D headline 학습은 순서상 보류합니다. 공개
aggregate는
[`results/aneumo_scaling_audit_20260803.json`](results/aneumo_scaling_audit_20260803.json)에
있습니다.

## 해석의 경계

현재 공개 데이터의 ruptured/unruptured label은 **cross-sectional rupture
status**입니다. 향후 2년/5년 파열 확률이 아니므로 논문·코드·사이트에서
이를 `future rupture risk`로 표현하지 않습니다. 외부·전향 검증 전까지
모든 결과는 연구용이며 임상 의사결정 도구가 아닙니다.
