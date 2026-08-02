# AURORA v1 모델 명세

상태: architecture contract

연결 설정: `configs/aurora_v1.json`

## 0. 아키텍처 분류

AURORA v1은 **GNN을 국소 geometry encoder로 사용하는 hybrid neural
operator**다. 다음 세 연산을 구분한다.

| 범위 | 연산 | 역할 |
|---|---|---|
| local surface | edge message-passing GNN | 인접 표면의 곡률·법선·neck 관계 encode |
| global anatomy | latent physics-token attention | 멀리 떨어진 inlet–sac–outlet 정보 교환 |
| continuous output | cross-attention query neural operator | 임의 volume/wall 좌표에서 cycle coefficient 복원 |

따라서 “GNN 기반”은 local stem을 설명할 때는 맞지만, 전체 모델을
autoregressive MeshGraphNet으로 분류하면 틀리다. 출력은 고정 mesh의
next-step node state가 아니라 BC-conditioned continuous field
distribution이다.

## 1. 입력과 출력

### 입력

| tensor | shape 예시 | 내용 |
|---|---:|---|
| `surface_pos` | `[Ns, 3]` | centerline-local frame의 surface point |
| `surface_feat` | `[Ns, 20]` | normal, curvature, radius, geodesic neck distance, node type |
| `edge_index` | `[2, Es]` | triangle 또는 kNN adjacency |
| `volume_query` | `[Nv, 3]` | interior collocation/query point |
| `anatomy_context` | `[Ca]` | site, parent diameter, branch count, scale |
| `bc_observed` | `[Cb]` or null | waveform basis, flow split, hematocrit/rheology |
| `clinical` | `[Cc]` | downstream head에서만 사용; operator geometry encoder와 분리 |

권장 pilot 크기는 `Ns=4096`, `Nv=8192`다. 원본 mesh를 이 크기로
강제 변환하는 것이 아니라, immutable mesh에서 reproducible sampling하고
mapping index를 저장한다.

### 출력

- `volume_coeff`: velocity/pressure temporal coefficients at volume queries
- `wall_coeff`: vector WSS temporal coefficients at surface queries
- `bc_samples`: sampled latent BC scenarios and weights
- `functional_samples`: TAWSS, OSI, LSA, RRT, neck/dome hotspot descriptors
- `status_probability`: case-level cross-sectional probability
- `status_interval`: calibrated interval or prediction set
- `abstain_score`: BC/OOD uncertainty에 기반한 research abstention flag

## 2. geometry normalization

global xyz를 그대로 넣지 않는다.

1. inlet–aneurysm–outlet centerline로 local longitudinal axis를 정한다.
2. aneurysm neck centroid를 origin으로 둔다.
3. parent-vessel diameter로 무차원화한다.
4. second axis는 neck normal 또는 bifurcation plane으로 정한다.
5. axis ambiguity와 reflection은 augmentation 및 consistency loss로 다룬다.

이 방식은 완전한 SE(3)-equivariance를 주장하지 않지만, 작은 데이터에서
e3nn 전체 stack보다 구현·검증이 단순하고 anatomical interpretation을
유지한다. 향후 strict equivariant baseline을 별도 비교한다.

## 3. module A — multi-scale geometry encoder

### Local stem

- kNN `k=16`
- edge feature: relative position/local-frame, distance, normal angle,
  curvature difference, geodesic distance difference
- 4 residual edge-message blocks: `64 → 96 → 128 → 192`
- boundary type별 learnable embedding

### Hierarchical tokens

- farthest-point/geodesic pooling: `4096 → 1024 → 256`
- neck, inlet, outlet, dome extreme point는 pooling에서 강제 보존
- 128 latent physics tokens, width 256
- 8 physics-attention blocks, 8 heads, MLP ratio 4

pooling score 자체를 novelty로 주장하지 않는다. anatomy preservation은
mesh decimation에 따른 hotspot 소실을 막기 위한 engineering constraint다.

## 4. module B — boundary-condition latent

BC를 geometry가 결정한다고 가정하지 않는다.

### Observed-BC mode

- inlet waveform을 8개 Fourier mode 또는 16개 PCA coefficient로 encode
- outlet flow split, Reynolds/Womersley proxy, rheology token을 결합
- 동일 case의 실제 BC를 decoder FiLM에 직접 주입

### Missing-BC mode

- empirical conditional prior `p(z_bc | anatomical site, diameter, branch
  topology)`에서 `K=8` scenario sample
- prior는 train fold의 BC만으로 적합
- geometry encoder가 prior를 지나치게 좁히지 못하도록 minimum variance와
  held-out BC coverage로 감시
- posterior `q(z_bc | field, known BC)`는 training-only inference network

초기 구현은 diagonal Gaussian mixture 4개로 시작한다. normalizing flow는
BC sample 수와 likelihood calibration이 충분할 때만 추가한다. 작은
clinical cohort에서 diffusion prior를 바로 쓰지 않는다.

## 5. module C — one-shot dual-domain decoder

### Temporal representation

cardiac cycle의 field \(h(x,t)\)를 다음처럼 출력한다.

\[
h(x,t)=a_0(x)+\sum_{k=1}^{8}
\left[a_k(x)\cos(2\pi kt/T)+b_k(x)\sin(2\pi kt/T)\right]
\]

80 timestep을 autoregressive하게 생성하지 않고 `2K+1=17` coefficient를
한 번에 생성한다. Fourier mode 수 4/8/12는 ablation한다.

### Coarse volume branch

- implicit query decoder: volume query ↔ physics token cross-attention
- outputs: `u_x,u_y,u_z,p` coefficient
- 512 random collocation point에서 divergence/momentum residual
- inlet/outlet flux와 no-slip boundary residual

### Fine wall branch

- original surface query의 local embedding과 multi-scale token을 결합
- vector WSS coefficient를 직접 출력
- neck/dome/high-curvature query를 oversample하되 evaluation은 area-weighted
- volume velocity gradient에서 얻은 WSS와 direct wall WSS의
  cross-consistency

volume branch는 물리적 전역 구조, wall branch는 gradient-sensitive
functional을 담당한다. 둘 중 하나만으로 충분한지는 ablation으로 확인한다.

## 6. module D — differentiable functionals

sample별로 복원한 cycle에서 계산한다.

- TAWSS
- OSI
- RRT
- low shear area fraction
- p95 WSS와 hotspot area/centroid
- neck inflow concentration proxy
- dome/neck/parent area-weighted summary

metric 정의와 epsilon, area weighting은 real CFD pipeline과 동일해야 한다.
source solver의 summary 정의를 확인하지 못하면 같은 이름을 사용하지 않고
`project_*` prefix를 붙인다.

## 7. module E — functional sufficiency head

clinical/morphology MLP와 distributional hemodynamic set encoder를 late
fusion하되, hemodynamic representation은 field branch와 공동 학습한다.

```text
clinical + morphology ── MLP(64, 32) ─────────┐
K functional samples ── set transformer(128) ─┼─ gated fusion ─ status logit
geometry global token ─ stop-gradient option ─┘
```

`geometry global token`은 direct path leakage를 확인하기 위해 기본
실험에서는 차단하고 별도 ablation에서만 허용한다. 그렇지 않으면 모델이
hemodynamics를 무시한 채 geometry로 status를 맞힐 수 있다.

real-CFD oracle head는 outer test fold를 보지 않고 inner training fold에서
학습한다. surrogate head는 다음을 보존한다.

- oracle logit KL 또는 temperature-scaled distillation
- case pair ranking
- calibration/Brier auxiliary

## 8. loss

\[
\mathcal L =
\lambda_f\mathcal L_{\mathrm{field}}+
\lambda_h\mathcal L_{\mathrm{functional}}+
\lambda_p\mathcal L_{\mathrm{physics}}+
\lambda_e\mathcal L_{\mathrm{energy}}+
\lambda_c\mathcal L_{\mathrm{consistency}}+
\lambda_t\mathcal L_{\mathrm{task}}
\]

초기 상대 weight는 config에 있지만 확정 hyperparameter가 아니다. inner
validation에서 작은 grid로 선택한다.

- `field`: area/volume-weighted normalized L1 + relative L2
- `functional`: log-scaled scalar error + hotspot Dice/centroid
- `physics`: divergence, flux balance, no-slip, optional momentum
- `energy`: generated field samples의 functional-space energy score
- `consistency`: volume-derived vs direct wall WSS
- `task`: real-CFD oracle distillation + pairwise ranking

physics residual를 넣었다는 이유로 “physics guaranteed”라고 표현하지 않는다.
residual은 numerical discretization과 collocation에 종속된 regularizer다.

## 9. inference modes

| mode | BC | 출력 | 용도 |
|---|---|---|---|
| A | observed | conditional field distribution | surrogate fidelity |
| B | missing | BC-marginal field distribution | geometry-only deployment study |
| C | partial | sparse waveform/flow proxy conditioned | practical bridge |
| D | CFD oracle | real field only | upper bound |

모든 결과 표는 mode를 명시한다. mode A 결과로 mode B 성능을 주장하지
않는다.

## 10. 구현 순서

1. deterministic steady wall-only operator
2. same-geometry multi-BC probabilistic wall operator
3. one-shot transient wall decoder
4. coarse volume auxiliary와 cross-consistency
5. CMHA functional fine-tuning
6. task-aligned head

한 번에 전체 모델을 만들지 않는다. 각 단계가 이전 단계보다 무엇을
개선했는지 같은 split과 compute budget에서 확인한다.
