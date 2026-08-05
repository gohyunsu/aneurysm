window.AURORA_DATA = Object.freeze({
  lineage: [
    {
      year: "2011–21",
      title: "Morphology + CFD association",
      copy: "형태·WSS·OSI와 rupture status의 연관성을 retrospective cohort에서 모델링했다.",
      status: "Peer reviewed · clinical association",
      url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC3021316/"
    },
    {
      year: "2021",
      title: "MeshGraphNet",
      copy: "Unstructured mesh의 encode–process–decode와 autoregressive simulation learning을 정립했다.",
      status: "ICLR · method foundation",
      url: "https://arxiv.org/abs/2010.03409"
    },
    {
      year: "2023–24",
      title: "GNOT & Transolver",
      copy: "Irregular geometry에서 operator transformer와 physics-aware tokenization을 확장했다.",
      status: "ICML · operator learning",
      url: "https://proceedings.mlr.press/v235/wu24r.html"
    },
    {
      year: "2025",
      title: "Aneumo & AneuG-Flow",
      copy: "Synthetic geometry와 다중 BC·대규모 CFD가 geometry–BC variation을 분리할 기반을 만들었다.",
      status: "NeurIPS dataset + preprint",
      url: "https://papers.nips.cc/paper_files/paper/2025/hash/e2b8ff0035bc9f572a7deefbcbea85bc-Abstract-Datasets_and_Benchmarks_Track.html"
    },
    {
      year: "2025–26",
      title: "Aneurysm graph surrogates",
      copy: "Inflow-aware physics GNN과 graph transformer가 transient field, WSS, OSI를 빠르게 근사했다.",
      status: "npj Digital Medicine + arXiv",
      url: "https://www.nature.com/articles/s41746-026-02404-z"
    },
    {
      year: "2025–26",
      title: "Probabilistic operators",
      copy: "Diffusion·flow matching·proper scoring rule이 function-space conditional distribution을 이미 모델링한다.",
      status: "ICLR / NeurIPS · direct method prior art",
      url: "https://openreview.net/forum?id=fcBMLJtCoc"
    },
    {
      year: "2026",
      title: "Boundary-indexed operator families",
      copy: "Varying BC의 operator family와 support 밖 비식별성을 정식화해 missing-BC 문제 제기 자체가 novelty가 아님을 보였다.",
      status: "AI&PDE at ICLR workshop · direct problem prior art",
      url: "https://openreview.net/forum?id=lDjWQ9UxRy"
    },
    {
      year: "2026.04–07",
      title: "Partial-input, conditioning & residual priors",
      copy: "AAAI LANO, NOP, conditioning operator, learned boundary extension, GNO와 DeltaPhi가 partial input·conditioning·residual learning 자체의 novelty를 제거했다.",
      status: "AAAI / NeurIPS + arXiv · direct scope threats",
      url: "https://ojs.aaai.org/index.php/AAAI/article/view/37001"
    },
    {
      year: "2021–24",
      title: "Active feature acquisition",
      copy: "Generative-surrogate AFA와 acquisition-conditioned oracle가 test-time feature 선택과 일반 decision cost를 이미 다룬다. Active BC 자체는 novelty가 아니다.",
      status: "ICML · mandatory decision baselines",
      url: "https://proceedings.mlr.press/v235/valancius24a.html"
    },
    {
      year: "2025",
      title: "Neural-operator functional Thompson sampling",
      copy: "NOTS가 unknown operator output의 known functional을 posterior operator sample로 최적화하고 regret bound를 제시했다. Functional operator acquisition 자체도 novelty가 아니다.",
      status: "NeurIPS · mandatory adapted control",
      url: "https://proceedings.neurips.cc/paper_files/paper/2025/hash/2f5fb82b8b593c548ed538a8d336d800-Abstract-Conference.html"
    },
    {
      year: "2024–25",
      title: "PDE uncertainty & conditional consistency",
      copy: "OOD PDE uncertainty와 neural-process의 marginal/conditional consistency가 이미 독립 연구 축을 이룬다.",
      status: "ICML / NeurIPS · required baselines",
      url: "https://openreview.net/forum?id=Y50K6DSrWo"
    },
    {
      year: "2026.07",
      title: "PINN multimodal rupture-status fusion",
      copy: "3D geometry, PINN hemodynamic descriptors, clinical variable을 결합한 직접 경쟁 preprint가 등장했다.",
      status: "arXiv · not peer reviewed",
      url: "https://arxiv.org/abs/2607.10530"
    }
  ],
  competition: [
    ["Deployment input", "Current field + inflow", "Current field + inflow token", "Geometry + prescribed BC", "Geometry + arbitrary BC observation mask"],
    ["BC uncertainty", "Point condition", "OOD waveform test", "Prescribed constraint", "One joint BC density, analytically conditioned"],
    ["Temporal model", "Autoregressive", "Autoregressive transformer", "Unsteady PINN", "Secondary one-shot choice after D0"],
    ["Primary fidelity", "Velocity rollout RMSE", "Field · WSS · OSI error", "Descriptor / status score", "Coherence + paired response + coverage"],
    ["Downstream task", "Not validated", "Risk metrics descriptive", "Late-fusion status", "Secondary only; current signal negative"],
    ["Primary gap", "Partial/missing condition", "Mask coherence", "Condition uncertainty", "Must beat generic probabilistic operators"]
  ],
  gates: [
    {
      id: "G0",
      title: "Asset integrity",
      copy: "Case mapping, units, boundary markers, label definition, license, patient split을 모두 확인한다.",
      state: "Blocking",
      blocking: true
    },
    {
      id: "G1",
      title: "Is condition–marginal coherence exact?",
      copy: "Fresh 5-seed G1s가 7개 frozen check를 모두 통과했다. 최악 density/end-to-end mean은 0.02863/0.02977였다. 과거 G1/G1r은 failed로 유지하고 data scale은 novelty로 세지 않는다.",
      state: "G1s passed · nonlinear strong-baseline test next",
      blocking: true
    },
    {
      id: "G2",
      title: "Does paired response improve?",
      copy: "N1b는 exact 1d0bd9c의 다섯 seed에서 50개 checkpoint를 test 전에 동결했다. AURORA validation full-BC/paired mean은 0.01347/0.01366이지만 DeltaPhi objective보다 좋은 seed는 0/5였다. 이는 test 자격이지 superiority가 아니다.",
      state: "N1c outer-test contract frozen · test/3D blocked",
      blocking: true
    },
    {
      id: "G3",
      title: "Is one-shot actually efficient?",
      copy: "D0b에서 train-only POD 17/25만 representation-eligible다. 같은 benchmark의 learned 비교는 exploratory이며 fresh transient confirmation이 필요하다.",
      state: "POD eligible · learned and fresh-data tests pending",
      blocking: false
    },
    {
      id: "G4",
      title: "Does the method generalize?",
      copy: "Controlled PDE, nonlinear PDE, irregular 3D 세 domain에서 같은 coherence·response mechanism이 유효해야 한다.",
      state: "Blocking AAAI claim",
      blocking: true
    }
  ],
  datasets: [
    {
      name: "Aneumo",
      role: "동일 geometry × 8 steady BC response pilot",
      provenance: "32 base family × 2 deformation staged · 64 cases/512 members verified"
    },
    {
      name: "AneuG-Flow",
      role: "selected steady/pulsatile operator pretraining",
      provenance: "geometry archive only · field absent"
    },
    {
      name: "BenchAnXplore",
      role: "105 semi-idealized transient reproduction 및 GNN baseline",
      provenance: "105 × 80 audited · DCT rejected · train-only POD eligible"
    },
    {
      name: "CMHA",
      role: "secondary real-CFD와 cross-sectional status diagnostic",
      provenance: "tables audited · exploratory increment negative · case map pending"
    },
    {
      name: "AneuX",
      role: "750 geometry/status external association stress test",
      provenance: "metadata/mesh found · no real CFD"
    }
  ],
  changes: [
    {
      date: "2026.08.05",
      category: "implementation",
      title: "N1c batch failures now preserve their traceback",
      copy: "첫 두 exact-source attempts는 hash verification과 동일 test marker 뒤 exit 1이었지만 PBS spool 때문에 traceback이 남지 않았다. Logging-fixed attempt 3에서 seed-0 metric 전 missing true_weights schema 오류를 확인했다. Frozen test context에 기존 analytic boundary law를 재적용하며 config·seed·metric은 바꾸지 않는다.",
      files: ["cluster/ssu_a6gpu_nonlinear_pde_n1c_outer_test.pbs", "experiments/run_nonlinear_pde_n1c_outer_test.py", "CHANGELOG.md"]
    },
    {
      date: "2026.08.05",
      category: "protocol",
      title: "N1c freezes the decision estimand before opening the test seed",
      copy: "Checkpoint manifest c66f651을 pin하고 context 0,4,…,188, condition 0, route common random numbers, outer 8×inner 32 acquisition, 2,000 context bootstrap을 고정했다. True oracle은 radius-2.5 truncated GMM conditional을 정확히 sampling한다. N1c source commit과 full contract 전에는 test를 생성하지 않는다.",
      files: ["configs/nonlinear_pde_n1c.json", "experiments/run_nonlinear_pde_n1c_outer_test.py", "src/aurora/nonlinear_pde_evaluation.py", "docs/experiment-protocol.md"]
    },
    {
      date: "2026.08.05",
      category: "experiment",
      title: "Five-seed N1b checkpoint manifest is frozen without opening test",
      copy: "Exact 1d0bd9c의 117/117 contract와 다섯 A6000 job이 모두 성공했다. 50개 learned checkpoint와 공통 train-only POD hash를 공개 manifest에 고정했다. Pair loss의 validation 방향은 pair-zero/random-pair/DeltaPhi 대비 4/5, 3/5, 2/5였고 combined objective는 DeltaPhi보다 0/5였다. N1은 미결정이며 별도 outer-test execution overlay 전 test context는 생성하지 않는다.",
      files: ["results/nonlinear_pde_n1b_checkpoint_manifest_20260805.json", "docs/experiment-protocol.md", "configs/aurora_v1.json", "CHANGELOG.md"]
    },
    {
      date: "2026.08.05",
      category: "implementation",
      title: "Fixed POD variation is separated from confirmatory model variation",
      copy: "938d6c2 seed 0–2는 test 없이 정상 완료됐지만 direct generic/NOP initialization이 fixed POD RNG state를 상속한 것을 감사에서 발견했다. 이 artifact는 runtime diagnostic으로만 보존한다. POD는 공유하되 model build 직전 각 confirmatory seed로 RNG를 reset한 새 exact source에서 5개를 모두 재실행한다.",
      files: ["src/aurora/nonlinear_pde_decision.py", "configs/nonlinear_pde_n1b.json", "docs/model-spec.md", "CHANGELOG.md"]
    },
    {
      date: "2026.08.05",
      category: "implementation",
      title: "N1b builds a test-locked strong-baseline checkpoint path",
      copy: "각 confirmatory seed job은 joint/independent/ACFlow/LANO completion, three shared-operator controls, DeltaPhi-style residual, generic/NOP POD-Gaussian을 train/validation만으로 고른다. POD-96은 training field만 사용하며 seed 73080601과 iteration 4를 공유한다. 10개 checkpoint hash가 모이기 전 test는 생성되지 않는다.",
      files: ["experiments/run_nonlinear_pde_n1b_checkpoint_freeze.py", "src/aurora/nonlinear_pde_decision.py", "cluster/ssu_a6gpu_nonlinear_pde_n1b_checkpoint_freeze.pbs", "configs/nonlinear_pde_n1b.json"]
    },
    {
      date: "2026.08.05",
      category: "experiment",
      title: "N1a selects the optimization contract; N1b freezes it before test",
      copy: "Exact eebcd91 A6000 run은 test context 0개로 종료됐다. Validation objective는 raw 1,400/2,800에서 0.05007/0.02071, scale-normalized 1,400/2,800에서 0.03732/0.01772였고, 고정 규칙은 마지막 variant를 선택했다. N1b는 이 선택만 고정하며 모든 strong-baseline checkpoint manifest가 public commit되기 전 test와 3D를 차단한다.",
      files: ["results/nonlinear_pde_n1_optimization_attribution_20260805.json", "configs/nonlinear_pde_n1b.json", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.05",
      category: "experiment",
      title: "Unit-peak core improves sharply but does not pass",
      copy: "Exact 54046a3 development seed는 full-BC/paired-response L2를 0.05771/0.05729까지 낮췄지만 unchanged 0.05를 넘었다. N1a는 raw/scale-normalized loss×1,400/2,800 step만 새 seed의 validation에서 비교하며 success threshold와 test/N1/3D 권한이 없다.",
      files: ["results/nonlinear_pde_n1_core_development_unit_peak_20260805.json", "configs/nonlinear_pde_n1_optimization_attribution.json", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.05",
      category: "result",
      title: "First N1 core development is not checkpoint-eligible",
      copy: "Exact 6075530 validation-only run에서 joint-density NLL은 -4.290이었지만 lifted operator full-BC/paired-response relative L2는 0.1739/0.1862였다. Test는 생성하지 않았다. Density로 operator failure를 덮지 않으며 unit-peak envelope로 동일 함수 클래스의 optimization conditioning만 두 번째 development seed에서 재검사한다.",
      files: ["results/nonlinear_pde_n1_core_development_20260805.json", "src/aurora/nonlinear_pde_decision.py", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.05",
      category: "implementation",
      title: "N1 tensor mismatch is stopped before metric generation",
      copy: "첫 PBS contract가 [B,1089] correction과 [33,33] envelope의 shape mismatch를 검출했다. Envelope만 [1089]로 flatten했고 seed·data·rank·loss·threshold·test rule은 바꾸지 않았다. Development metric은 생성되지 않았으며 새 exact SHA contract만 채택한다.",
      files: ["src/aurora/nonlinear_pde_decision.py", "tests/test_nonlinear_pde_decision.py", "docs/server-execution.md", "CHANGELOG.md"]
    },
    {
      date: "2026.08.05",
      category: "implementation",
      title: "N1 core runner is validation-only by construction",
      copy: "Joint full-covariance 2-GMM, truncated BC sampler, chunked semilinear solver와 exact Dirichlet-lifted rank-96 operator를 구현했다. 첫 runner는 train/validation만 생성하고 test access와 N1 decision을 false로 기록한다. Strong-baseline 전체 비교 전에는 result로 해석하지 않는다.",
      files: ["src/aurora/nonlinear_pde_decision.py", "experiments/run_nonlinear_pde_n1_development.py", "cluster/ssu_a6gpu_nonlinear_pde_n1_development.pbs", "tests/test_nonlinear_pde_decision.py"]
    },
    {
      date: "2026.08.05",
      category: "research",
      title: "N1 freezes a decision-consequence test, not an architecture claim",
      copy: "NOTS 때문에 neural-operator functional acquisition과 generic regret를 novelty에서 제외했다. N1은 같은 최종 physical-condition mask의 route posterior가 Bayes action과 one-component value-of-information에 만드는 손실을 검증한다. 5-seed rule과 LANO/NOP/ACFlow/ACO/NOTS-style strong controls를 test 전에 고정했다.",
      files: ["configs/nonlinear_pde_n1.json", "docs/research-direction.md", "docs/model-spec.md", "docs/experiment-protocol.md", "docs/literature-lineage.md"]
    },
    {
      date: "2026.08.05",
      category: "result",
      title: "Fresh context-stratified N0r passes 9/9 numerical checks",
      copy: "N0a outcome 전에 동결한 exact contract를 37d31a8에서 실행했다. 세 fresh seed의 worst nonlinear departure 0.01933, grid error 0.00375, worst-component response 0.17484, route residual 8.94e-8로 전 항목을 통과했다. N0 실패는 보존하며 N1 상세 사전등록만 열고 method novelty와 irregular-3D는 계속 차단한다.",
      files: ["results/nonlinear_pde_n0r_20260805.json", "docs/research-direction.md", "docs/experiment-protocol.md", "configs/aurora_v1.json", "site/assets/research-data.js"]
    },
    {
      date: "2026.08.05",
      category: "experiment",
      title: "N0r is frozen independently of the N0a outcome",
      copy: "N0a metric 전 commit 1a68053에서 fresh seed와 context-stratified selector를 고정했다. Reference 24개는 24 context를 각각 한 번, paired 48개는 각각 두 번 포함한다. PDE·BC law·solver·functionals·threshold·worst-seed rule은 N0와 동일하며 pass는 N1 protocol 등록만 허용한다.",
      files: ["configs/nonlinear_pde_n0r.json", "src/aurora/nonlinear_pde_reentry.py", "cluster/ssu_a6gpu_nonlinear_pde_n0r.pbs", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "result",
      title: "N0a supports context-sampling attribution, not a gate pass",
      copy: "Exact 749f596의 24×12 all-context run에서 failed seed의 contiguous/stratified/all-case median은 0.00774/0.01221/0.01828이었다. 다른 seed도 stratified median 0.01624/0.01811을 보였다. 그러나 former reference 이상인 context는 18–19/24라 uniform nonlinearity는 아니다. N0는 failed로 유지하고 24-context fresh-seed N0r만 연다.",
      files: ["results/nonlinear_pde_n0_attribution_20260803.json", "docs/research-direction.md", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "N0a audits every context without reopening the gate",
      copy: "Failed N0의 세 seed 각각에서 24 context×12 condition 전체 semilinear–linear departure를 계산한다. 원래 contiguous 12-case와 12-context stratified statistic, 전체 context-median 분포를 비교하지만 success threshold가 없고 N0 relabel·N1/3D 실행·N0r seed/threshold 선택은 모두 금지한다.",
      files: ["configs/nonlinear_pde_n0_attribution.json", "src/aurora/nonlinear_pde_attribution.py", "cluster/ssu_a6gpu_nonlinear_pde_n0_attribution.pbs", "docs/experiment-protocol.md"]
    },
    {
      date: "2026.08.03",
      category: "result",
      title: "Frozen nonlinear N0 fails one of nine checks",
      copy: "Exact 0ead687의 3-seed A6000 run은 solver·grid error·8-component response·effective rank·functional diversity·analytic conditioning을 통과했지만 seed별 nonlinear departure 0.02319/0.02365/0.00727 중 최악 값이 frozen 0.01 기준을 넘지 못했다. N1/3D는 차단한다. Context-major contiguous slice는 실패를 소급 변경하지 않으며, threshold-free N0a와 fresh-seed context-stratified N0r로만 원인을 분리한다.",
      files: ["results/nonlinear_pde_n0_20260803.json", "docs/research-direction.md", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "N0 contract failure corrected before scientific metric access",
      copy: "첫 dependency-complete PBS contract job은 GMM tensor API 오류로 exit 1을 반환했다. N0 metric job은 제출하지 않은 채 tensor path를 교정하고, 선언된 a∈[0.7,1.3], λ∈[8,40] envelope와 outward diffusive flux −a∂ₙu를 코드에 일치시켰다. Seed·sample count·threshold·decision rule은 바꾸지 않았다.",
      files: ["configs/nonlinear_pde_n0.json", "src/aurora/nonlinear_pde.py", "tests/test_nonlinear_pde.py", "docs/experiment-protocol.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "N0 freezes the nonlinear problem before any learned comparison",
      copy: "33/65 nested grid에서 variable-diffusivity semilinear PDE, 8-component edge BC, context-conditioned 2-GMM을 고정했다. 세 seed의 residual·discretization·nonlinear departure·all-component response·effective rank·functional diversity·analytic conditioning을 모두 통과해야 N1을 등록한다. Active acquisition 자체는 선행연구이며 N0는 method evidence가 아니다.",
      files: ["configs/nonlinear_pde_n0.json", "src/aurora/nonlinear_pde.py", "cluster/ssu_a6gpu_nonlinear_pde_n0.pbs", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "result",
      title: "G1s passes all seven frozen exact-data checks",
      copy: "Exact b0e555a의 fresh 5-seed A6000 run에서 worst density/end-to-end mean 0.02863/0.02977, coverage errors 0.00836/0.01294, projective CI upper 0.000674로 모두 통과했다. G1/G1r은 failed로 보존하며 data quantity는 contribution이 아니다. 다음은 nonlinear N0이며 통과 뒤 N1에서 LANO·NOP·generic probabilistic/AFA baseline을 비교한다.",
      files: ["results/controlled_pde_g1s_20260803.json", "docs/research-direction.md", "docs/experiment-protocol.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "G1s freezes a fresh data-adequacy sanity before execution",
      copy: "이전 G1/G1r/DA1/DA2와 겹치지 않는 5개 seed, original empirical NLL, 3,072×8 training budget을 고정했다. G1r model·optimizer·validation/test size·metric·threshold는 모두 유지한다. Pass는 next-domain 실행 권한일 뿐 novelty나 과거 gate relabel이 아니다.",
      files: ["configs/controlled_pde_g1s.json", "src/aurora/controlled_pde_sufficiency_gate.py", "docs/experiment-protocol.md", "cluster/ssu_a6gpu_controlled_g1s.pbs", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "result",
      title: "DA2 rejects a negligible shrinkage win and retains data adequacy",
      copy: "고정 rule은 768×8에서 shrinkage 0.50을 골랐지만 empirical NLL 대비 평균 개선은 0.05444→0.05431(0.23%)뿐이고 1/3 seed에서 악화됐으며 population NLL도 더 나빴다. 반면 3,072×8 original empirical NLL은 평균 0.02575, 최악 0.02706이었다. Shrinkage는 method가 아니며 다음 fresh exact test는 data adequacy만 검증한다.",
      files: ["results/controlled_pde_density_development_20260803.json", "docs/research-direction.md", "docs/model-spec.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "DA2 freezes a sample-only estimator development comparison",
      copy: "세 새 development seed에서 empirical NLL과 grouped unbiased/shrinkage 0.25/0.50을 동일 network·optimizer로 비교한다. 원래 G1r budget인 768×8에서 estimator를 선택하고 3,072×8은 data-sufficiency control로만 쓴다. 모든 checkpoint는 sampled validation NLL로 선택하며 DA2에는 threshold가 없다.",
      files: ["configs/controlled_pde_density_development.json", "src/aurora/controlled_pde_density_development.py", "cluster/ssu_a6gpu_controlled_density_development.pbs", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "result",
      title: "DA1 rules out density capacity as the primary bottleneck",
      copy: "Exact cf675af의 A6000 30-task run에서 analytic population-NLL은 최악 density-only error 0.00495를 회복했지만 empirical NLL은 0.04401–0.04855였다. Fixed-axis 결과는 geometry와 repeated condition이 모두 필요함을 보였고, matched 6,144-record 비교의 768×8 우위는 3-seed descriptive 결과로만 남긴다. G1/G1r은 계속 failed다.",
      files: ["results/controlled_pde_density_attribution_20260803.json", "docs/research-direction.md", "docs/model-spec.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Density attribution separates capacity, objective noise, and sample allocation",
      copy: "G1/G1r과 겹치지 않는 세 diagnostic seed에서 true-parameter regression, analytic population NLL, empirical NLL을 같은 density network로 비교한다. 6,144 boundary sample을 고정한 192×32, 768×8, 3,072×2와 fixed-axis cells를 등록했다. Success threshold가 없으며 G1/G1r을 relabel할 수 없다.",
      files: ["configs/aurora_v1.json", "configs/controlled_pde_density_attribution.json", "src/aurora/controlled_pde_density_attribution.py", "cluster/ssu_a6gpu_controlled_density_attribution.pbs", "docs/model-spec.md", "docs/experiment-protocol.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Strong physical scaling leaves nontrivial velocity response only",
      copy: "Exact e12ff0a의 train-only audit에서 same-case anchor와 tuned global power까지 허용했다. Velocity는 Q^1.075 뒤 residual 0.2112, family-bootstrap CI95 [0.2001, 0.2243]로 0.15 기준을 통과했다. Pressure는 Q^1.75에서 0.1369 [0.1190, 0.1496]로 실패했다. Nonlinear N0/N1을 먼저 검증하며 future 3D G2는 velocity-only다.",
      files: ["results/aneumo_scaling_audit_20260803.json", "configs/aurora_v1.json", "configs/aneumo_scaling_audit_v1.json", "docs/model-spec.md", "docs/experiment-protocol.md", "docs/research-direction.md"]
    },
    {
      date: "2026.08.03",
      category: "data",
      title: "Aneumo selective cache is integrity-complete before learning",
      copy: "사전등록한 32 base family × 2 deformation의 512 member만 range-read해 64 case × 8 condition × 4,096 node cache를 완성했다. Split 20/6/6 family와 40/12/12 case, finite field, coordinate contract와 cache SHA-256을 검증했다. Learned G2 전에 train-only same-case-anchor physical-scaling audit을 고정했으며 raw/compact field는 재배포하지 않는다.",
      files: ["configs/aneumo_g2_pilot_v1.json", "configs/aneumo_scaling_audit_v1.json", "src/aurora/aneumo_scaling_audit.py", "docs/data-acquisition.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Prospective G1r completes and fails the absolute mean gate",
      copy: "Exact commit 951ace1의 fresh 5-seed run에서 coverage, full-BC operator, analytic nesting, IID-floor-calibrated projective 검사는 통과했다. 그러나 최악 seed density-only mean 0.07533과 end-to-end quadrature mean 0.07518이 고정 기준 0.05를 넘었다. 상대 baseline 개선으로 판정을 바꾸지 않고 density representation·optimization·data sufficiency를 먼저 분해한다.",
      files: ["results/controlled_pde_g1r_20260803.json", "docs/experiment-protocol.md", "docs/model-spec.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Fresh-test G1r is prospectively frozen before execution",
      copy: "Failed G1은 그대로 보존한다. 겹치지 않는 5개 fresh seed, validation-only density/operator checkpoint selection, analytic density moment·coverage, Gauss–Hermite end-to-end mean, matched-IID-floor projective CI와 absolute threshold를 실행 전에 고정했다.",
      files: ["configs/controlled_pde_g1r.json", "src/aurora/controlled_pde_reentry.py", "docs/experiment-protocol.md", "cluster/ssu_a6gpu_controlled_g1r.pbs"]
    },
    {
      date: "2026.08.03",
      category: "data",
      title: "Aneumo paired-BC pilot is family-disjoint and preregistered",
      copy: "ZIP64 range audit에서 geometry당 8 steady mass-flow condition과 internal NPY CRC·좌표·field contract를 확인했다. 32 AneuX base family × 2 deformation을 family-disjoint하게 고정하고 필요한 member만 선택 수집한다. Compact field는 재배포하지 않으며 이 pilot은 C2만 지원한다.",
      files: ["configs/aneumo_g2_pilot_v1.json", "src/aurora/aneumo_range.py", "docs/data-acquisition.md", "docs/experiment-protocol.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "D0b retains train-only POD but not learned superiority",
      copy: "105-case D0b에서 POD-17은 full L2 0.00141, bulge L2 0.00880, peak error 0.000764로 모든 frozen 기준을 충족했고 POD-25도 통과했다. DCT-II 17/25는 탈락했다. 다만 전체 benchmark가 architecture discovery에 쓰였으므로 같은 데이터의 learned 비교는 exploratory이며 G3 확인에는 fresh transient cases가 필요하다.",
      files: ["results/benchanxplore_d0b_20260803.json", "configs/aurora_v1.json", "docs/experiment-protocol.md", "docs/model-spec.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "G1b separates a flawed raw metric from remaining density error",
      copy: "K=128 learned direct-vs-nested distance 0.1006은 iid floor 0.1013과 구분되지 않았고 analytic moment residual은 7.45e−9였다. 그러나 K=2048 missing-mask end-to-end mean error 0.0853 중 density-only가 0.0754로 남아 frozen G1은 닫힌 상태다. Coverage attribution도 아직 unresolved다.",
      files: ["results/controlled_pde_g1b_20260803.json", "docs/research-direction.md", "docs/experiment-protocol.md", "AGENTS.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Equal-budget D0b passes implementation and leakage smoke",
      copy: "17/25 coefficient DCT-II와 5-fold train-only POD의 two-pass audit을 구현했다. Pinned container에서 orthonormality, span reconstruction, held-out covariance exclusion, synthetic full runtime을 통과했으며 실제 105-case 결과 전에는 temporal branch를 선택하지 않는다.",
      files: ["configs/benchanxplore_d0b.json", "src/aurora/benchanxplore_d0b.py", "tests/test_benchanxplore_d0b.py", "cluster/ssu_a6gpu_benchanxplore_d0b.pbs"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Failed-G1 attribution diagnostic is implementation-complete",
      copy: "Frozen G1의 같은 model·seed·split을 재학습해 K=128/512/2048 iid distance floor, 양방향 nested Gaussian factorization, sampling/BC-density/operator conditional-mean error를 분해하도록 구현했다. Pinned container의 tensor test와 축소 end-to-end smoke를 통과했으며 이 진단은 G1을 재개방하지 않는다.",
      files: ["configs/controlled_pde_g1b_diagnostic.json", "src/aurora/controlled_pde_diagnostic.py", "tests/test_controlled_pde_diagnostic.py", "cluster/ssu_a6gpu_controlled_g1b.pbs"]
    },
    {
      date: "2026.08.03",
      category: "model",
      title: "Temporal contract removes the failed fixed-Fourier decoder",
      copy: "문서만이 아니라 machine-readable model contract와 상세 가이드에서도 K=8 Fourier를 제거했다. D0b는 동일한 17/25 coefficient budget에서 DCT-II와 train-geometry-only POD를 비교하며, 통과 전에는 one-shot temporal branch가 없다.",
      files: ["configs/aurora_v1.json", "docs/model-spec.md", "docs/experiment-protocol.md", "site/learn.html"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Frozen D0 and exact-G1 gates both fail",
      copy: "D0 K=8은 full L2 1.62%, bulge L2 6.16%로 실패했고 K=12도 bulge 기준을 넘었다. Exact G1은 direct mask baseline보다 모든 mask에서 개선됐지만 absolute mean·coverage·raw projective gate를 통과하지 못했다. 두 실패를 그대로 보존하고 G1b estimator-floor 진단과 equal-budget D0b만 exploratory로 진행한다.",
      files: ["results/benchanxplore_d0_attempt2_20260803.json", "results/controlled_pde_g1_attempt2_20260803.json", "docs/experiment-protocol.md"]
    },
    {
      date: "2026.08.03",
      category: "research",
      title: "Direct-prior red team separates coherence from OOD correctness",
      copy: "2026 conditioning-gap, Neural Operator Processes, learned boundary extension, Generalized Neural Operator를 추가 감사했다. Partial/missing BC의 ID coherence와 calibration, supplied full-BC extrapolation, shifted hidden-law detection을 분리해 식별 불가능한 OOD coverage 주장을 제거했다.",
      files: ["docs/literature-lineage.md", "docs/research-direction.md", "docs/experiment-protocol.md", "paper/"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Queued G1 corrected before any GPU execution",
      copy: "첫 exact-G1 submission은 실행 전 Q 상태에서 geometry-bootstrap CI 직렬화 누락을 발견해 취소했다. 2,000회 cluster bootstrap과 95% CI를 구현하고 pinned-container smoke를 통과한 새 SHA만 재제출한다.",
      files: ["src/aurora/controlled_pde.py", "tests/test_controlled_pde.py", "CHANGELOG.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Exact controlled-PDE G1 preregistered and runtime-smoked",
      copy: "Correlated random Dirichlet BC를 갖는 exact Poisson family에서 learned joint BC density, analytic arbitrary-mask conditioning, shared operator, paired response loss를 5 seeds로 평가하도록 metric과 threshold를 결과 전에 고정했다. Pinned container의 축소 runtime smoke를 통과했다.",
      files: ["configs/controlled_pde_g1.json", "src/aurora/controlled_pde.py", "cluster/ssu_a6gpu_controlled_g1.pbs"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "D0 attempt 1 ended at the scheduler walltime",
      copy: "Frozen BenchAnXplore D0의 첫 실행은 30분 32초에 scheduler exit −29로 종료돼 metric이 생성되지 않았다. 과학적 verdict는 unresolved로 유지하고, 동일 threshold로 60분 재실행과 비식별 case-count progress를 준비했다.",
      files: ["results/benchanxplore_d0_attempt1_20260803.json", "cluster/ssu_a6gpu_benchanxplore_d0.pbs", "src/aurora/benchanxplore.py"]
    },
    {
      date: "2026.08.03",
      category: "research",
      title: "Novelty reset to coherent partial-condition operators",
      copy: "직접 선행연구 감사 결과 missing-BC 문제, probabilistic operator, GNN+physics, Fourier decoder를 독립 novelty에서 제외했다. 임의 BC observation mask의 nested condition–marginal coherence, same-geometry paired response, structural/model uncertainty separation을 primary method로 재정의했다.",
      files: ["AGENTS.md", "docs/research-direction.md", "docs/model-spec.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "BenchAnXplore one-shot representation gate preregistered",
      copy: "105 geometry × 80 timestep archive를 검증하고, 모델 학습 전 Fourier 4/8/12-mode oracle loss로 one-shot 표현 가능성을 판정하는 D0와 K=8 threshold를 고정했다. 이후 selective 64-case Aneumo cache와 velocity scaling eligibility, G1s exact pass를 확보했다. Learned 3D는 nonlinear N0/N1 strong baseline 뒤에만 진행한다.",
      files: ["configs/benchanxplore_d0.json", "src/aurora/benchanxplore.py", "cluster/ssu_a6gpu_benchanxplore_d0.pbs"]
    },
    {
      date: "2026.08.03",
      category: "site",
      title: "Production field guide and aggregate result verified",
      copy: "Content commit c9a998b의 quality와 GitHub Pages workflow가 성공했고, production main·11장 상세 가이드·aggregate G1 JSON의 HTTP 200 응답을 확인했다.",
      files: ["CHANGELOG.md", "site/learn.html", "results/cmha_g1_exploratory_20260803.json"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "CMHA G1 exploratory signal does not support real-CFD increment",
      copy: "99명/105병변 patient-grouped 5×5 linear sensitivity에서 C+M AUPRC 0.759, C+M+H 0.717, Δ −0.0419 [−0.1083, 0.0066]을 관찰했다. 공식 case map이 없어 confirmatory G1은 unresolved로 유지하고 C3를 conditional secondary로 낮췄다.",
      files: ["results/cmha_g1_exploratory_20260803.json", "docs/experiment-protocol.md", "docs/research-direction.md"]
    },
    {
      date: "2026.08.03",
      category: "data",
      title: "Aneurysm asset registry audited on introai9",
      copy: "Aneumo, AneuG-Flow, BenchAnXplore, CMHA, AneuX, Aneurisk 자산을 읽기 전용으로 확인했다. CMHA의 99 patient/105 lesion 구조와 불명확한 PHASE·ELAPSS leakage 후보를 식별했다.",
      files: ["docs/server-execution.md", "docs/datasets.md", "AGENTS.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Scheduler GPU execution established on junjinyong",
      copy: "Pinned container와 PBS A6000 allocation에서 CUDA smoke, patient-grouped unit/data smoke, 5-repeat G1 sensitivity를 실행하고 commit·config·environment·manifest·status·metrics artifact를 남겼다.",
      files: ["cluster/", "experiments/", "src/aurora/cmha_pilot.py"]
    },
    {
      date: "2026.08.03",
      category: "site",
      title: "Zero-assumption field guide adds eleven detailed windows",
      copy: "동맥류·CFD부터 mesh/graph, GNN, hybrid operator, missing BC, temporal basis, functionals, datasets, literature gap, experiment gates, server provenance까지 독립 URL과 용어집으로 확장했다.",
      files: ["site/learn.html", "site/assets/learn.css", "site/assets/learn.js"]
    },
    {
      date: "2026.08.03",
      category: "research",
      title: "Private manuscript repository separated from public research code",
      copy: "원고, claim–evidence matrix, planned result table, 내부 writing history를 private gohyunsu/aneurysm-paper로 분리하고 public commit SHA pin 규칙을 만들었다.",
      files: ["aneurysm-paper/AGENTS.md", "paper/", "docs/CLAIM_MATRIX.md"]
    },
    {
      date: "2026.08.03",
      category: "research",
      title: "Primary question reset to missing-BC functional sufficiency",
      copy: "단순 In-PI-MGN 개선을 중단하고 geometry-only deployment의 비식별성을 연구 중심으로 이동했다. Endpoint를 cross-sectional rupture status로 제한했다.",
      files: ["docs/research-direction.md", "AGENTS.md", "README.md"]
    },
    {
      date: "2026.08.03",
      category: "model",
      title: "AURORA v1 architecture contract",
      copy: "Multi-scale geometry tokens, empirical BC latent, one-shot temporal basis, dual volume/wall decoder, task-aligned functional head를 명세했다.",
      files: ["docs/model-spec.md", "configs/aurora_v1.json"]
    },
    {
      date: "2026.08.03",
      category: "research",
      title: "Falsifiable gate and nested evaluation protocol",
      copy: "Real-CFD incremental utility를 첫 gate로 두고, geometry/patient split, mandatory direct-geometry baseline, calibration, risk-retention을 사전 정의했다.",
      files: ["docs/experiment-protocol.md", "src/aurora/protocol.py", "tests/test_protocol.py"]
    },
    {
      date: "2026.08.03",
      category: "site",
      title: "Research hub rebuilt as one decision narrative",
      copy: "반복적인 dataset 페이지 중심 구조를 thesis, lineage, architecture, gates, paper blueprint, filterable decision history의 단일 흐름으로 재구성하고 CI link/anchor 검증을 추가했다.",
      files: ["site/index.html", "site/assets/aurora.css", "site/assets/aurora.js", "scripts/check_site.py", ".github/workflows/quality.yml"]
    },
    {
      date: "2026.07.17",
      category: "research",
      title: "Raw dataset audit and provenance tooling",
      copy: "BenchAnXplore, AneuX, CMHA, Aneurisk의 source asset을 직접 점검하고 manifest·preview·inventory 도구와 재현 기록을 추가했다.",
      files: ["scripts/", "docs/datasets.md", "site/assets/"]
    },
    {
      date: "2026.07.17",
      category: "site",
      title: "Initial Aneurysm AI research hub",
      copy: "Clinical imaging, CFD surrogate, dataset integration을 설명하는 최초 GitHub Pages 구조와 dataset notebook을 공개했다.",
      files: ["site/", "index.html", "README.md"]
    }
  ]
});
