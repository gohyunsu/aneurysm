# AneuX-derived transient-CFD material source audit

> **Frozen decision · schema 8.3 · 2026-08-11 KST:** a previously unaudited
> Hugging Face record materially changes the public source inventory: its
> metadata names transient CFD for selected side-wall and bifurcation AneuX
> geometries. It does **not** identify a paper-ready task. The strongest of six
> fresh formulations scores **28.0/40**, below the unchanged 32-point
> admission line. All six are rejected. No terms were accepted; no field,
> mesh, tensor, archive, P0/P1, method, architecture, scientific-server query,
> PBS/GPU job, outer test, result row or paper claim is authorized.

## 1. Adjudication of the supplied surface-vector analysis

The supplied analysis is correct on the decisive points:

- job `115645.ECE-util1` remains `E`/exit 2, GPU 0,
  `execution-incomplete / no scientific verdict`, with 0/10 registered checks
  evaluated;
- its exact 32.0/40 score is immutable source history, not model evidence;
- the same contract is not repaired or rerun, and it opens no P1, method,
  architecture, GPU, outer test or contribution;
- field-error-matched structural disagreement is a falsifiable application
  question, whereas GNN, Hodge, equivariance, edge 1-forms, topology loss and
  tracking are components or controls rather than novelty;
- task stability and failure-mechanism evidence must precede architecture
  development.

Two corrections are necessary. First, the public and shared `AGENTS.md` files
already describe the job as closed; there is no stale running experiment to
repair. Second, exact critical-point coordinates and cardiac-cycle worldlines
are too fragile to be the first estimand. A boundary-margin signed total degree
with abstention is safer, but even that is only a possible estimand and its
separate P0 is also closed without a scientific verdict. Neither formulation
is an active paper identity.

## 2. What the new metadata actually establishes

The canonical
[`yiyings/transient-dataset`](https://huggingface.co/datasets/yiyings/transient-dataset)
record and the older `yiyings/sidewall-transient-cfd` API alias resolve to the
same exact revision
`38c574bc54a1ead9a4830da09ae5087e42b9d6c2`, last modified
2026-06-20. The official metadata says that the geometries are derived from
the [AneuX morphology database](https://doi.org/10.5281/zenodo.6678442) and
that the authors generated transient CFD for selected side-wall and
bifurcation aneurysms.

The API metadata, without opening a data member, exposes:

| Item | Exact public-metadata observation |
|---|---|
| Access | public repository metadata, manual gate; contact sharing required |
| License tag | `CC-BY-NC-4.0`; original AneuX terms also apply |
| Repository entries | 1,940 total: root metadata entries plus 1,938 case-file paths |
| Topology folders | 180 bifurcation and 143 side-wall folders |
| Unique visible IDs | 322, not 323; `SNF365` occurs in both topology folders |
| Files per folder | `blood_data.pt`, `wall_data.pt`, `dome_sac.ply`, `forward_fusion_info.npz`, `inlet_centroids.csv`, `merged_reconstruction_remeshed.obj` |
| File-type counts | 646 `.pt`; 323 each `.ply`, `.npz`, `.csv`, `.obj` |
| Sorted sibling-manifest SHA-256 | `7874b4520d455f8921317ad1d97de7614d1ed95185df2b77f6bce40e39c6508d` |
| Topology-qualified case-manifest SHA-256 | `53d0f8145b69f42ec630703fff27282a1e562009fa6b0136488ee5172cb6d5c3` |
| Unique-ID manifest SHA-256 | `2693754f1de732289ac5d15b94061dfe2815bca2bfe126da1c5460fb7ae5a648` |

The API reports `usedStorage=1,381,031,461,556` bytes. This is a repository
storage-accounting field, not a verified sum of the current payload members,
so it is not reported as an archive byte count. The raw README route and
commit-history route both required authenticated gated access. The public card
does not specify tensor keys, WSS association, units, phase count or alignment,
boundary conditions, solver settings, convergence, coordinate correspondence,
patient/base-family mapping, train/validation/test split or a linked model
repository. Filename similarity to AneuG-Flow is a provenance clue, not proof
that the tensors share its schema.

Accordingly, 323 folders cannot be called 323 patients. The strongest count
available from public metadata is 322 unique visible lesion-like IDs. Even
that does not establish patient independence or prevent same-patient and
same-base-family leakage.

## 3. Direct-prior boundary

The material release improves asset plausibility, but the proposed method
space is already dense.

- [AneuG-Flow](https://papers.nips.cc/paper_files/paper/2025/file/e2b8ff0035bc9f572a7deefbcbea85bc-Paper-Datasets_and_Benchmarks_Track.pdf)
  already defines large-scale synthetic steady/transient aneurysm CFD and WSS
  baselines with the same high-level tensor filenames.
- [RHSIA](https://arxiv.org/abs/2601.19876) already predicts cardiac-cycle
  surface WSS with a graph Transformer, temporal conditioning, graph-harmonic
  geometry descriptors and steady-flow augmentation. A transient WSS graph
  Transformer, GHD representation or steady-to-transient transfer is not a
  residual contribution.
- [Physics-Constrained GNN for real-time aneurysm hemodynamics](https://www.nature.com/articles/s41746-026-02404-z)
  already covers autoregressive mesh prediction, physical constraints and
  unseen inflow conditions on the BenchAnXplore family.
- [Multiphysics learning for aneurysm thrombosis](https://doi.org/10.1016/j.compbiomed.2026.111649)
  uses Transformer GNNs for multiple CFD-derived fields and explicitly tests
  unseen inflow/cardiac-cycle behavior. Its 101 two-dimensional sections share
  an idealized parent-vessel construction and do not provide clinical
  thrombosis truth, but it further removes architecture-combination novelty.
- Hodge/HSD, SE(3)-equivariant transient WSS, robust critical-point tracking,
  trajectory-preserving vector-field compression and aneurysm-specific
  cardiac-cycle critical-point analysis remain mandatory direct controls.

The new record therefore does not revive the statement “GNN/Hodge/topology
loss improves MSE” as a contribution. A defensible study would still require
an observed, stable failure that these controls do not explain.

## 4. Frozen eight-axis screen

Axes remain fixed in this order: biomedical-imaging importance, target
identifiability, residual novelty after direct priors, usable asset readiness,
effective independent-unit strength, strong-baseline feasibility,
interpretable-figure value and ISBI-schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Topology-stratified side-wall↔bifurcation transient-WSS generalization | 4.5 | 3.0 | 1.5 | 2.5 | 4.0 | 5.0 | 5.0 | 2.5 | **28.0** | reject |
| Structure-faithful transient surface-WSS on AneuX geometries | 4.5 | 2.0 | 2.0 | 2.5 | 4.0 | 5.0 | 5.0 | 2.5 | **27.5** | reject |
| Field/function-concordant TAWSS–OSI–RRT surrogation | 4.5 | 3.0 | 1.0 | 2.5 | 4.0 | 5.0 | 5.0 | 2.5 | **27.5** | reject |
| Remeshing-robust surface-vector transport | 4.0 | 3.5 | 0.5 | 2.5 | 4.0 | 5.0 | 4.5 | 3.0 | **27.0** | reject |
| Inflow-conditioned out-of-distribution transient operator | 4.5 | 1.5 | 1.5 | 2.5 | 4.0 | 5.0 | 5.0 | 2.0 | **26.0** | reject |
| Topology-selective conformal structural certificate | 4.5 | 2.0 | 1.0 | 2.5 | 4.0 | 5.0 | 4.5 | 2.5 | **26.0** | reject |

The leading cross-topology formulation is attractive for figures and strong
controls, but side-wall/bifurcation labels alone do not define a new learning
problem. Public metadata does not show whether boundary conditions, source
cohorts or patient families differ systematically between the two groups.
Without those semantics, a topology split can measure source or CFD-pipeline
confounding rather than geometric generalization. Domain-stratified evaluation
is also required hygiene, not a method contribution.

## 5. Consequence for architecture and evidence order

This record is a **material source-change signal**, not an E0 pass. It is not
the same source contract as the closed AneuG P0, and it cannot repair or rerun
that contract. Because the fresh source score is below 32, accepting the gate
or learning the tensor schema would not retroactively authorize P0 or training.
A future revision would need a new, prospectively scored evidence version with
at least:

1. an official schema for tensor keys, units, phases, BC and solver provenance;
2. lesion→patient/base-family lineage and topology-qualified split keys;
3. an explicit license/terms decision by the user;
4. a linked benchmark or code contract sufficient to reproduce strong
   RHSIA, equivariant, Hodge/HSD and Cartesian/projected controls;
5. a residual estimand whose novelty survives those controls.

Only then could a new method-free gate ask whether tangent fields, degree,
critical points or trajectories are stable. If stability and a matched
baseline failure were later observed, the smallest candidate would compare
Cartesian, tangent-projected and oriented-edge outputs on the same strong
backbone. Hodge and equivariance remain baselines; critical-point/worldline
losses remain prohibited until the target is demonstrably stable.

## 6. Operational boundary

- Active source lead, shortlist, primary problem, method, architecture, P0/P1,
  GPU, outer test, result row and submission identity remain zero.
- No Hugging Face terms or contact-sharing agreement was accepted. No gated
  file or raw README was opened.
- The exact dataset revision is added to the fail-closed public source watch.
  A revision/access/license/manifest change can request only a fresh source
  re-audit; it cannot download data or select a model.
- No scientific server or scheduler was queried and no job was created.
  Future gate-authorized execution is restricted to `introai9` PBS.
  `junjinyong` remains prohibited for connection, query, transfer, submission
  and monitoring; login-node GPU commands remain prohibited.
