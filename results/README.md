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

G1b는 G1을 대체하거나 재개방하지 않는다.

현재 temporal representation 결과:

- `benchanxplore_d0_attempt2_20260803.json`: fixed Fourier K=8 실패,
  K=12도 bulge 기준 실패
- `benchanxplore_d0b_20260803.json`: DCT-II 탈락, train-only POD
  rank 17/25 representation screen 통과

D0b 통과는 learned one-shot 성능이나 novelty를 뜻하지 않는다. 같은
105-case benchmark의 후속 learned 비교는 exploratory이며 fresh transient
confirmation이 필요하다.
