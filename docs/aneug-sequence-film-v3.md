# Sequence and predicted-steady FiLM comparator

This is the direct **comparator** described in [Sheng et al., III-F](https://arxiv.org/html/2601.19876v2),
not the proposed selective-transfer model. Model and two-stage training code
exist; no real-data sequence/FiLM training result follows from that fact.

New full-training comparisons use the explicit [size-preserving input
profile](aneug-geometry-scale-v3.md). The earlier per-case radius normalization
discarded size from coordinate/normal-only inputs. Keep its curves as a
different input condition, not as evidence against the published comparator.
The correction changes neither model capacity nor WSS targets.

## Source identity and explicit adaptations

The pinned AneuG-Flow tree is `4a090a0f12538deef6fcea88b81afe78ce38152e`.
Its `new_version/models/UniversalNaiveUNets.py` supplies generic graph U-Net
building blocks; `transient_cycle.py` is a dual-head U-Net, and
`multitaskunet_w_fouriers.py` is a different spatial/temporal modal model. None
is silently relabelled as the paper's complete-sequence/predicted-steady FiLM
control. The pinned tree has no explicit runnable class for that control.

Our reimplementation follows the paper's stated operations: Chebyshev graph
convolutions on the registered mesh hierarchy, node-wise geometry features,
waveform cross-attention, MLP complete-cycle output, and optional predicted-
steady FiLM. It does not vendor author source or claim the author's exact
hyperparameters, normalization, implementation or published performance.

`configs/aneug_sequence_film_model_v3.json` records the source-scale recipe:

- Encoder widths 64/128/256, global context 2048, decoder widths 512/128;
  15 genuine PyG ChebConv layers, Chebyshev order 3. Intermediate widths are
  also explicit. The global max-context MLP has no normalization, a declared
  difference from the released generic PyG MLP's default batch normalization.
- Published-family inputs are coordinates/normals plus supplied topology and
  waveform. An optional 439-channel geometry/GHD information-control exists;
  it is not silently enabled in the paper-described input condition.
- Three-neighbor inverse-squared-distance interpolation uses actual per-case
  geometry. Chunked Torch distances replace the compiled neighbor dependency,
  not graph convolutions. Edges are the registered mesh edges, never a newly
  constructed Euclidean-neighbor graph. No learned encoding is cached.
- Two eight-head cross-attention blocks operate from node queries to 80
  temporal/waveform tokens, followed by a 128/64/240 MLP. No N-by-N self-
  attention is added. Depths, head count, FiLM location and widths are explicit
  choices where the paper does not provide a complete sequence recipe.
- Waveform U-Net/time encoding reuses the documented RHSIA reimplementation.
  The staged repeating waveform uses the same nominal index-resampling and
  0.8-period convention, not a claim that physical timestamps were recovered.
- FiLM is applied to fused node features before the cycle MLP. It receives
  physical steady predictions divided by a fixed admitted-training scale:
  `h -> (1 + gamma(predicted_steady)) * h + beta(predicted_steady)`.

The output is one physical Cartesian `[80, N, 3]` WSS field, without enforced
tangency, Fourier truncation, cycle-mean tying or separate TAWSS/OSI heads.
The last phase is valid and is not forced equal to the first.

## Two-stage training, not oracle conditioning

`SteadyWSSPredictor` is trained separately on the existing admitted steady
stream. `train_steady_prior` visits only supplied eligible rows under a recorded
fixed exposure budget and physical area-weighted single-field objective.
It records terminal weights, epoch histories, optimizer/scheduler/RNG recovery
states and exact exposures; no transient-validation choice selects this prior.
Hash-bound epoch continuation preserves sampling order and stochastic state.

The sequence model then uses `train_cycles` and the common physical evaluator.
The prior is frozen and remains in eval mode, including buffers, during
transient training. It receives a geometry-only mapping, never actual steady
CFD. The geometry encoder/readout/attention initializations are seed-paired
between the T and FiLM variants; the additional FiLM parameters initialize
after common parameters. Private execution must verify actual pretraining
provenance before treating a supplied prior as a valid scientific comparator.

The separate runtime supports full 584/73 development, not yet subset-specific
label-efficiency preprocessing. It reuses the existing 13,985-row stream and
407 exclusions without requiring the 13.6-GB RHSIA spectral-encoder asset,
which this sequence input condition does not use. Fixed-budget pretraining is
not a claim of convergence; choose actual budgets using measured full-size
cost and learning curves, then allow recorded extensions where needed.

## Fair reporting and current limits

Count steady pretraining, transient cycle/phase supervision, updates, both
models' parameters and frozen-prior forward passes separately. A frozen prior
forward is compute, not a fresh steady label exposure. Complete-cycle inference
includes both geometry encoders; the old v2 discarded-head/no-overhead claim
does not apply. A separate warmed inference benchmark remains necessary.

The private two-stage runtime preserves the raw common cycle result (whose
stage-local steady exposure count is zero) and writes a separate comparison
summary with pretraining costs. It does not rewrite the common result to hide
which stage consumed labels. Manuscript/results/identifiers remain private.

Tests include genuine Cheb message passing, full-scale default widths, all 80
outputs, geometry-only inference traps, waveform dependence, node permutation,
three-neighbor interpolation, all active gradients, a frozen prior with mutable
normalization buffers, paired initialization, actual steady-then-cycle synthetic
training and dropout/optimizer-exact steady continuation. These are code and
training-path tests, not GPU timing, baseline convergence or model superiority.
