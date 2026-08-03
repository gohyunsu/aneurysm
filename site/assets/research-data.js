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
      copy: "G1r은 mean gate로 실패했다. Threshold 없는 post-result 진단이 true-parameter, population-NLL, matched-budget geometry×condition scaling으로 원인을 분리한다.",
      state: "G1/G1r failed · density attribution registered",
      blocking: true
    },
    {
      id: "G2",
      title: "Does paired response improve?",
      copy: "Train-only strong scaling audit에서 velocity residual은 0.2112 [0.2001, 0.2243]로 통과했지만 pressure는 0.1369 [0.1190, 0.1496]로 실패했다.",
      state: "Velocity-only eligible · learned G2 still blocked by G1r",
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
      date: "2026.08.03",
      category: "experiment",
      title: "Density attribution separates capacity, objective noise, and sample allocation",
      copy: "G1/G1r과 겹치지 않는 세 diagnostic seed에서 true-parameter regression, analytic population NLL, empirical NLL을 같은 density network로 비교한다. 6,144 boundary sample을 고정한 192×32, 768×8, 3,072×2와 fixed-axis cells를 등록했다. Success threshold가 없으며 G1/G1r을 relabel할 수 없다.",
      files: ["configs/controlled_pde_density_attribution.json", "src/aurora/controlled_pde_density_attribution.py", "cluster/ssu_a6gpu_controlled_density_attribution.pbs", "docs/experiment-protocol.md"]
    },
    {
      date: "2026.08.03",
      category: "experiment",
      title: "Strong physical scaling leaves nontrivial velocity response only",
      copy: "Exact e12ff0a의 train-only audit에서 same-case anchor와 tuned global power까지 허용했다. Velocity는 Q^1.075 뒤 residual 0.2112, family-bootstrap CI95 [0.2001, 0.2243]로 0.15 기준을 통과했다. Pressure는 Q^1.75에서 0.1369 [0.1190, 0.1496]로 실패했다. 따라서 future G2는 velocity-only이며 learned 3D 실행은 G1r 실패 때문에 계속 보류한다.",
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
      copy: "105 geometry × 80 timestep archive를 검증하고, 모델 학습 전 Fourier 4/8/12-mode oracle loss로 one-shot 표현 가능성을 판정하는 D0와 K=8 threshold를 고정했다. 당시 Aneumo는 1 geometry × 2 BC sample뿐이어서 full G2를 blocked로 유지했다. 이후 selective 64-case cache를 별도 검증했지만 learned G2는 여전히 physical-scaling audit과 exact sanity에 의해 blocked다.",
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
