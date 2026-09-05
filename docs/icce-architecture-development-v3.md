# ICCE 2027: direct-baseline and architecture development

Status: active development objective, adopted 2026-09-05. This supersedes the
supervision-only paper identity, not the provenance of earlier experiments.
No numerical result or clinical generalization claim is made here.

## Question and deliverable

Can explicitly separating transferable spatial information from transient-only
periodic response improve geometry-to-complete-cycle vector WSS over strong
direct priors and ordinary shared-representation training?

The deliverable is a reproducible, evidence-backed paper, not a particular
winning architecture or completion of the historical 72-cell grid. The current
target is [ICCE 2027 CSH](https://icce.org/2027/), submission September 15, 2026.
The [official instructions](https://icce.org/2027/submission-guidelines/) allow
up to six US-letter IEEE conference pages. Website maintenance stays inactive.

## Source fidelity comes before architecture ranking

| Comparator | Implementation identity and role |
|---|---|
| Sheng/RHSIA Graph Transformer + masked steady samples | Highest-priority direct prior. Reconcile published equations, released feature encoders and executable training path. |
| Sheng sequence decoder + predicted-steady FiLM | Direct control for transferring a predicted steady prior, not a new proposal. |
| Existing separated GHD/GPS-GINE | Internal reference for additional architecture gains; not an exact RHSIA reproduction. |
| LinearNO | Official-source general-geometry operator with an explicitly documented WSS input/output adaptation. |
| Existing Transolver | Reuse only where input, split, objective, selection and exposure provenance actually match. |
| Official AneuG Graph U-Net | Released dataset baseline; its steady benchmark value is not a transient result. |
| LaB-GATr transient WSS | Assess official implementation feasibility and geometric value, then include as a strong geometric control. |

Fresh upstream tree checks on 2026-09-05 resolve AneuG-Flow to
`4a090a0f12538deef6fcea88b81afe78ce38152e` and LinearNO to
`3f2b80df13c17a09e250f2ebe4d4ecdfd4acf269`. AneuG exposes GraphGPS and
GPSUNet classes, but its released `train_baselines.py` does not instantiate
either. A class existing in the tree does not establish an executable,
publication-matched reproduction.

Source inspection also identifies temporal endpoint masking and feature
handoff questions in the AneuG implementation. Reproduce them on synthetic
inputs before making a failure claim or changing the author code. Log any
correction separately; do not deliberately benchmark a defective path. No
top-level code license was detected in either tree: do not vendor author code
into this repository on that basis. Keep source checkouts external and pinned;
document permissions needed for redistribution independently of reproducibility.

The historical `T_plus_S_shared_decoder` predicts a cycle and applies steady
supervision to its temporal mean. It is specifically a **mean-tied control**,
not Sheng's masked-time training. Its result cannot establish that all decoder
sharing is inferior. Preserve result labels/bytes; clarify their interpretation.

## Minimal development ladder

1. Reconcile and exercise direct-prior implementations; preserve native temporal
   conditioning and feature semantics as far as the source permits.
2. Add a simple missing-time/regime control to the current geometry encoder.
   Its purpose is to challenge separated heads, not to stand in for RHSIA.
3. Audit the actual source phase grid and train-only Fourier reconstruction.
   Compare the existing output with a Fourier-only decoder before adding gates.
4. Compare ordinary task adapters, always-shared transfer, and geometry/mode-
   selective transfer under the same spatial backbone and information budget.
5. Expand promising comparisons to paired seeds and label budgets, and compile
   the final manuscript from verified evidence.

The prospective candidate shares learned spatial operations, while keeping the
steady output, transient mean response and transient oscillatory response
distinct. It never equates steady WSS to the transient mean or a cardiac phase.
Transient mode-dependent routing is a hypothesis to test, not established
novelty. No true steady CFD is an inference input. Keep one physical WSS field;
TAWSS/OSI are derived from it. Tangency projection and functional losses are
separate factors, not proposal-only privileges.

`aneug_cycle_decoders.py` supplies the first **controls**, not the complete
candidate: a missing-time shared snapshot decoder and a real periodic decoder.
Both have synthetic tests, no file loading and no embedded scientific split.
The Fourier implementation includes the single even-grid Nyquist column and
requires explicit, uniform, nonduplicated period-fraction coordinates. It does
not assume that phase 79 equals phase 0. Its reconstruction helper reports an
oracle representation error, never learned-model performance.

The missing-time control masks its learned temporal vector after the biased
MLP, includes all valid indices through T-1, and uses one physical output scale
for both regimes. It omits the source waveform CNN and spectral geometry
encoders; call it an internal control. A head-free fresh geometry encoder is
required so unused parameters are not silently counted or trained.

## Fairness, selection and resource policy

- Keep official transient membership and duplicate-component geometry splits.
  Never split phases, resampled meshes or augmentations across partitions.
- Keep the audited steady exclusions and training-only transformations. Report
  official-release counts separately from processed-object counts.
- Separate transient-only from transient-plus-steady information. Record
  exposures, unique cases, optimizer updates, tuning budget, parameter count,
  training memory/time and full-cycle inference cost; none is a substitute for
  the others. Give baselines reasonable optimization before judging them.
- Use a limited initial candidate set and paired development seeds, then spend
  the larger budget on the final candidate and strongest comparator. No
  arbitrary absolute accuracy admission threshold is introduced.
- Reuse old terminals where comparable; do not promote historical selected-
  checkpoint runs to fixed-final-epoch results or vice versa.
- Existing in-flight useful jobs may finish. Unsubmitted historical sensitivity
  work is lower priority than direct baselines and architecture tests. Revisit
  queued jobs once a runnable replacement is ready; log cost and relevance,
  not favorable/unfavorable metrics, as the reason for a queue change.
- Repairs and reruns are allowed with recorded cause, code/config change and
  fresh output paths. Preserve all valid results, including negative ones.

Primary endpoint remains physical vector-WSS relative L2; same-field TAWSS and
valid-reference-support OSI are secondary. Use paired geometry-level estimates
and crossed seed/case uncertainty, not vertices or phases as independent cases.
Frequency-specific errors explain the representation; they do not replace the
primary endpoint or justify output smoothing at an unreported accuracy cost.

## Evidence and writing boundary

The original test was already opened for the original method pair. New
architecture development uses train/validation; any subsequent old-test
assessment is explicitly an additional, adaptively motivated evaluation, not
untouched confirmation. Reshuffling observed cases does not manufacture a fresh
test. Independent evidence is desirable but its absence is reported, not used
as a reason to freeze all development.

The fixed waveform and registered synthetic mesh domain do not establish
patient-, hospital-, topology- or boundary-condition generalization. Measure
the actual inference path: a revised architecture cannot inherit an old
zero-overhead or real-time claim. Real surface figures must share coordinates,
cameras and scales across reference and methods, with transparent case choice.

Write one chain: direct-prior gap -> required structural difference -> controlled
comparison -> mechanism ablation -> label/compute evidence -> limitations.
If an ordinary model is equally good, select it and revise the contribution.

## Primary sources for the next implementation audit

- [Sheng et al. v2, methods III-C--F](https://arxiv.org/html/2601.19876v2)
- [AneuG-Flow official code](https://github.com/WenHaoDing/AneuG-Flow)
- [LinearNO, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/37003)
- [LinearNO official code](https://github.com/HiPRL/LinearNO)
- [Rygiel et al., transient WSS](https://arxiv.org/html/2507.22817v1)
- [LaB-GATr application code](https://github.com/PatRyg99/AAA-WSS-neural-surrogate)
- [F-Adapter](https://arxiv.org/abs/2509.23173)
- [Multi-fidelity Laplace neural operators](https://arxiv.org/abs/2502.00550)

Frequency representations, generic adapters, residual correction, GNNs and
steady augmentation are prior art. The proposed selective-transfer mechanism
still needs both a closest-prior comparison and executed supporting evidence.
