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
      copy: "Proper scoring rule과 latent conditioning으로 output function-space uncertainty를 모델링했다.",
      status: "Method preprints · component prior art",
      url: "https://arxiv.org/abs/2502.12902"
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
    ["Deployment input", "Current field + inflow", "Current field + inflow token", "Geometry + prescribed BC", "Geometry; observed / partial / missing BC"],
    ["BC uncertainty", "Point condition", "OOD waveform test", "Prescribed constraint", "Conditional field distribution"],
    ["Temporal model", "Autoregressive", "Autoregressive transformer", "Unsteady PINN", "One-shot cycle basis"],
    ["Primary fidelity", "Velocity rollout RMSE", "Field · WSS · OSI error", "Descriptor / status score", "Field + functional + coverage"],
    ["Downstream task", "Not validated", "Risk metrics descriptive", "Late-fusion status", "Real-CFD functional sufficiency"],
    ["Primary gap", "Missing-BC deployment", "Missing-BC calibration", "Uncertainty + nested sufficiency", "Must prove all three"]
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
      title: "Does real CFD add information?",
      copy: "CMHA에서 clinical+morphology+real CFD가 clinical+morphology보다 incremental AUPRC를 보이는지 먼저 확인한다.",
      state: "First experiment",
      blocking: true
    },
    {
      id: "G2",
      title: "Is the operator calibrated OOD?",
      copy: "Held-out geometry와 held-out BC에서 field, functional, 90% coverage를 동시에 검증한다.",
      state: "Pre-clinical gate",
      blocking: true
    },
    {
      id: "G3",
      title: "Does the surrogate retain CFD signal?",
      copy: "G1의 분모가 양수일 때만 risk-retention을 계산하고 target 0.75, minimum 0.50을 사전 등록한다.",
      state: "Conditional",
      blocking: false
    },
    {
      id: "G4",
      title: "Is hemodynamics non-redundant?",
      copy: "Direct geometry-to-status보다 낫지 않으면 hemodynamic bridge라는 주장을 철회한다.",
      state: "Falsification",
      blocking: false
    }
  ],
  datasets: [
    {
      name: "Aneumo",
      role: "동일/유사 geometry × 8 steady BC로 sensitivity pilot",
      provenance: "synthetic CFD"
    },
    {
      name: "AneuG-Flow",
      role: "selected steady/pulsatile operator pretraining",
      provenance: "synthetic CFD"
    },
    {
      name: "BenchAnXplore",
      role: "105 semi-idealized transient reproduction 및 GNN baseline",
      provenance: "synthetic CFD"
    },
    {
      name: "CMHA",
      role: "patient-specific real-CFD bridge와 G1 downstream gate",
      provenance: "real CFD"
    },
    {
      name: "AneuX",
      role: "750 geometry/status external association stress test",
      provenance: "no real CFD"
    }
  ],
  changes: [
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
