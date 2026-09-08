# AGENTS.md — AURORA research code

## Current objective

Prepare a defensible IEEE ICCE 2027 CSH paper, using at most six IEEE
conference pages, about complete-cycle aneurysm surface vector-WSS prediction.
The research question is whether separating transferable spatial operations
from transient-specific periodic response improves accuracy and label
efficiency against strong direct-prior models. Architectural novelty is a
research objective, not an assumed result. A simpler model should replace
the candidate if the evidence favors it.

Read `docs/icce-architecture-development-v3.md` for the research plan and
the relevant model documentation before changing an implementation. Current
results, manuscript, operational history and execution state are maintained
privately; this public file is not a live experiment ledger.

## Data and scientific scope

- Use the official AneuG-Flow 730-case transient cohort and existing
  584/73/73 train/validation/test partition. Keep all 80 phases of a geometry
  together; preserve overlap exclusions and source provenance.
- Distinguish the paper's 14,000 steady cases from the processed archive's
  14,392 rows and audited 13,985-row eligible pool.
- The additional 79 processed-only cases are not part of the main cohort or
  an independent external test set.
- Fit preprocessing only on admitted training cases. For nested
  58/146/292-case experiments, refit subset GHD/WSS/geometry statistics and
  pass the same transforms explicitly to eligible steady and validation
  inputs. At 100%, the existing audited 584-case reader/transforms may be
  reused; a redundant refit is not mandatory.
- A decoder normalizer needed to recover physical archive values is not a
  newly fitted predictive statistic. Disclose that distinction.
- The original test partition was already opened. Later development or
  evaluation cannot be presented as an untouched confirmatory test, and
  repartitioning the same cases does not restore independence.
- Synthetic geometry, registered connectivity and a fixed waveform limit
  generalization. Do not claim independent-patient, boundary-condition,
  arbitrary-mesh or clinical rupture-risk performance without evidence.

## Candidate and direct comparisons

The candidate uses multiresolution geometry features, a shared
geometry-conditioned spatial kernel bank, transient-only location/frequency
routing, and one full-cycle vector-WSS output. Its real Fourier representation
retains all 80 coefficients; it is not spectral compression. Do not equate
steady WSS with a transient phase or cycle mean. Actual steady CFD is not an
inference input.

Prioritize adequate, faithful direct comparisons:

- Sheng/RHSIA graph transformer with correctly masked steady augmentation.
- Complete-sequence prediction and a separately trained, predicted-steady
  FiLM prior; distinguish original geometry-only and information-matched
  variants and count prior training/inference cost.
- Existing regime-separated GHD–GPS/GINE and official AneuG Graph U-Net.
- Original-core LinearNO and reusable Transolver comparisons.
- Original-core LaB-GATr as a geometric strong control, with explicit task
  adaptation and native phase-conditioned execution.

Do not relabel a steady-to-cycle-mean shared head as RHSIA masked training.
A regime-token joint-training control is a distinct comparison. Distinguish
original implementation, faithful reimplementation and task adaptation.
A +GHD adaptation does not automatically inherit end-to-end equivariance.

Required structural contrasts include the existing model, Fourier-only
decoder, ordinary task-specific adapter, uniform spatial sharing and
selective sharing. A frequency-independent geometry-routing control separates
frequency conditioning from location dependence. Report real capacity
differences; do not add inactive parameters to manufacture a match.

Fourier bases, residuals, attention, adapters and tangent projection are
established tools. Compare F-Adapter and multi-fidelity operators explicitly.
Do not add Hodge, topology, physics or uncertainty components without a
demonstrated role.

Relevant implementation guides:

- `docs/aneug-surface-transfer-v3.md`
- `docs/aneug-surface-transfer-training-v3.md`
- `docs/aneug-rhsia-comparator-v3.md`
- `docs/aneug-rhsia-snapshot-training-v3.md`
- `docs/aneug-rhsia-conditioning-v3.md`
- `docs/aneug-sequence-film-v3.md`
- `docs/aneug-labgatr-surface-v3.md`
- `docs/aneug-linearno-adaptation-v3.md`
- `docs/aneug-geometry-scale-v3.md`
- `docs/aneug-cycle-label-efficiency-v3.md`
- `docs/aneug-cycle-error-spectrum-v3.md`

## Evaluation and claims

Rank development candidates by validation mean physical vector-WSS rL2
point estimate. A paired interval containing zero is not a rejection gate.
Report uncertainty, TAWSS, valid-support OSI and measured cost alongside the
ranking; point-estimate leadership is not established statistical or universal
superiority.

Separate transient-only from transient-plus-steady information conditions.
Match split, permitted inputs, preprocessing, evaluator and reasonable tuning
opportunity. Report cycle/phase/steady exposures, optimizer updates, parameters,
training time, memory and complete 80-phase inference cost separately.
Equal updates or exposures do not imply equal compute.

Use adequate baseline learning curves before imposing performance judgments.
After development, pursue multiseed retraining, preferably five paired seeds
for the final candidate and strongest comparator, plus nested label-efficiency
curves. Case-level intervals from one selected seed do not estimate seed
variability. Reused endpoints must match model, seed, recipe, information,
selection and exposure contract; historical protocol results are not silently
transplanted.

TAWSS and OSI come from the same predicted field. Preserve the evaluator's
support, denominator and zero-prediction conventions. Temporal error analysis
must use complete-bin accounting and distinguish reference reconstruction
from learned prediction error. Actual surface figures use disclosed case
selection, aligned cameras and common color scales. Do not claim real-time,
consumer-device performance or CFD speedup without measurement.

## Implementation, execution and publication

- Preserve valid results and deployed source snapshots. Use fresh, explicitly
  versioned executions for changed science; do not overwrite results.
- Repairs, continuation and reruns are allowed when their reason and changes
  are recorded. Avoid duplicate submissions, but do not invent absolute
  no-repair rules or make a historical experiment grid the research goal.
- Preserve optimizer, scheduler, RNG, sampler and prior identity on recovery.
  Missing/discarded cost is unknown, not zero. A reused frozen steady prior
  must not silently incur repeated supervision.
- Test the actual changed behavior in proportion to risk, including
  production-width paths where appropriate. Small synthetic tests do not
  certify full-resolution CUDA execution or scientific performance.
- Routine scoped Git publication and new experiment deployment are approved.
  Keep exact source/activation identities and run relevant public Quality and
  private Integrity checks before deployment. Revalidate target ownership,
  live work and payloads; this does not authorize bypassing access controls,
  touching unrelated jobs, or rewriting already published history.
- Keep manuscripts, numerical results, private splits/manifests, checkpoints,
  team exports and operational metadata in the private research repository or
  approved private evidence storage. Never commit credentials or raw medical
  data. Do not add server/account names, host paths or live job handles to
  new public documentation.
- Public website maintenance is discontinued. Do not restart it.
- Keep this file concise and current. Historical operational records belong
  privately; stale history must not override the current user goal.
