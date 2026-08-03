# Aggregate research results

이 디렉터리는 공개 가능한 **aggregate exploratory result**만 버전 관리한다.

포함:

- 실행 code commit과 protocol 상태
- cohort 전체 수와 class count
- patient-grouped aggregate metric과 bootstrap CI
- GPU/container version
- 해석 제한과 다음 결정
- metric이 생성되지 않은 scheduler failure의 비식별 상태·exit·walltime

제외:

- source patient identifier
- row-level label·prediction·split
- 내부 서버 경로와 job endpoint
- raw table checksum과 protected asset
- checkpoint와 log 전체

`exploratory` 결과는 confirmatory gate 통과로 해석하지 않는다. 공식 case
mapping, feature provenance, 사전 정의 model family와 protocol을 모두
확인한 run만 confirmatory로 승격한다.

현재 controlled-PDE 결과:

- `controlled_pde_g1_attempt2_20260803.json`: frozen G1 실패
- `controlled_pde_g1b_20260803.json`: raw estimator floor와
  density/operator/MC attribution만 수행한 post-result diagnostic
- `controlled_pde_g1r_20260803.json`: fresh seed와 validation-only
  selection을 고정한 prospective re-entry 실패
- `controlled_pde_density_attribution_20260803.json`: threshold 없이
  capacity, finite-condition noise와 geometry×condition allocation을 분리한
  post-result DA1

G1b는 G1을 대체하거나 재개방하지 않는다.
G1r도 coverage·operator·analytic nesting·iid-floor 보정 projective 항은
통과했지만, 최악 seed의 density-only mean 0.07533과 end-to-end
quadrature mean 0.07518이 사전 기준 0.05를 넘었다. 상대 baseline 개선으로
이 absolute 실패를 덮지 않으며 nonlinear/3D confirmatory 학습은 계속
보류한다.

DA1에서는 같은 density network가 analytic population NLL로 최악
density-only error 0.00495를 회복했지만 empirical NLL은
0.04401–0.04855였다. Fixed-axis scaling은 geometry 수와 반복 condition
수가 모두 오차를 줄임을 보였다. 이 attribution은 새 gate가 아니며,
development-only estimator 선택 뒤 별도 fresh exact sanity가 필요하다.

현재 temporal representation 결과:

- `benchanxplore_d0_attempt2_20260803.json`: fixed Fourier K=8 실패,
  K=12도 bulge 기준 실패
- `benchanxplore_d0b_20260803.json`: DCT-II 탈락, train-only POD
  rank 17/25 representation screen 통과

D0b 통과는 learned one-shot 성능이나 novelty를 뜻하지 않는다. 같은
105-case benchmark의 후속 learned 비교는 exploratory이며 fresh transient
confirmation이 필요하다.

현재 Aneumo response-eligibility 결과:

- `aneumo_scaling_audit_20260803.json`: 20 train base family·40 case만 읽은
  사전등록 strong physical-scaling audit
- velocity: tuned \(Q^{1.075}\) residual 0.2112,
  family-bootstrap CI95 [0.2001, 0.2243] · channel eligibility 통과
- pressure: gauge-removed tuned \(Q^{1.75}\) residual 0.1369,
  CI95 [0.1190, 0.1496] · eligibility 실패

이는 같은-case anchor field까지 사용하는 강한 물리 baseline 뒤에도
velocity response가 남는다는 train-only 결과다. Learned model 성능이나
G2 통과가 아니며, failed G1/G1r 때문에 3D confirmatory training은
허용되지 않는다.
