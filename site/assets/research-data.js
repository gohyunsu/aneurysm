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
      status: "ICLR · direct problem prior art",
      url: "https://openreview.net/forum?id=lDjWQ9UxRy"
    },
    {
      year: "2026.04–07",
      title: "Conditioning gap, NOP & explicit-BC operators",
      copy: "CNP conditioning gap, partial-observation Neural Operator Processes, learned boundary extension과 Generalized Neural Operator가 직접 경쟁 범위를 좁혔다.",
      status: "TMLR + arXiv · direct scope threats",
      url: "https://arxiv.org/abs/2606.22946"
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
      copy: "정답 conditional distribution을 계산할 수 있는 controlled PDE에서 mean, coverage, nested-mask tower property를 먼저 검증한다.",
      state: "Frozen gate failed · attribution diagnostic next",
      blocking: true
    },
    {
      id: "G2",
      title: "Does paired response improve?",
      copy: "ID partial/missing에서는 calibration을, supplied full-BC support shift에서는 field와 같은-형상 ΔH를, hidden-law shift에서는 detection/abstention을 각각 검증한다.",
      state: "Full paired-BC asset blocked",
      blocking: true
    },
    {
      id: "G3",
      title: "Is one-shot actually efficient?",
      copy: "D0 oracle gate와 learned compute-matched 비교를 모두 통과할 때만 Fourier cycle decoder를 유지한다.",
      state: "K=8 failed · fixed Fourier rejected",
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
      role: "전체 release 확보 후 동일 geometry × 8 steady BC sensitivity",
      provenance: "현재 1 geometry × 2 BC sample only"
    },
    {
      name: "AneuG-Flow",
      role: "selected steady/pulsatile operator pretraining",
      provenance: "geometry archive only · field absent"
    },
    {
      name: "BenchAnXplore",
      role: "105 semi-idealized transient reproduction 및 GNN baseline",
      provenance: "105 × 80 HDF5/XDMF audited · D0 ready"
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
      copy: "105 geometry × 80 timestep archive를 검증하고, 모델 학습 전 Fourier 4/8/12-mode oracle loss로 one-shot 표현 가능성을 판정하는 D0와 K=8 threshold를 고정했다. Aneumo는 현재 1 geometry × 2 BC sample뿐이라 full G2를 blocked로 유지한다.",
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
