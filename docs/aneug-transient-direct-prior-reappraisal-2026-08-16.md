# AneuG transient-WSS direct-prior reappraisal · 2026-08-16

**Status:** direction-only, non-executable reappraisal. D6 remains registered
but not activated. No real field, validation or outer-test value was read; no
architecture, loss, checkpoint or GPU run was selected. The public static site
is outside the current workflow.

## Verdict

A performance-only AneuG transient-WSS paper is already occupied. The current
ISBI direction survives only as a narrower application/evaluation question:

> On held-out synthetic-geometry components, can a surrogate with apparently
> strong vector-field accuracy still misestimate cardiac-cycle WSS functionals,
> and can a same-backbone, moment-consistent cycle readout reduce that error
> without materially degrading the physical transient field?

This is not a new-GNN claim. Graph U-Nets, GraphGPS/GINE, GHD encodings,
LaB-GATr/LaB-VaTr, phase conditioning, sequence and spectral decoders, tangent
projection, steady-data augmentation, TAWSS/OSI/RRT computation and generic
exact output correction are all prior art or controls. AURORA has no active
paper identity until D6 passes and a separately registered baseline experiment
observes the proposed failure under a field-error-matched comparison.

## Direct prior that changes the boundary

### Same dataset and task

[Sheng et al., arXiv:2601.19876v2](https://arxiv.org/abs/2601.19876) already
train a GHD-enabled GraphGPS/GINE model to predict full-cycle vector WSS on
AneuG-Flow. They compare Graph U-Net, LaB-GATr, LaB-VaTr, a full-sequence
surrogate and a 512-mode spectral surrogate; augment pulsatile training with
14,000 steady cases; and derive TAWSS, OSI and RRT. Their manuscript uses a
random 9:1 train/test division, says 808 pulsatile cases, and reports for the
best model:

| Quantity | Reported value |
|---|---:|
| WSS MSE | 0.179 |
| maximum-normalized field \(rL_2^*\) | 2.84% |
| conventional field \(rL_2\) | 26.98% |
| TAWSS \(rL_2\) / \(rL_2^*\) | 13.54% / 3.81% |
| OSI \(rL_2\) / \(rL_2^*\) | 68.35% / 5.34% |
| RRT \(rL_2\) / \(rL_2^*\) | 17.31% / 2.62% |

The paper also observes late-diastolic error, smoothing of OSI, sequence-model
averaging near peak systole and suppression of true high-frequency features by
spectral low-pass projection. Consequently, none of the following is a valid
AURORA contribution: transient WSS on AneuG, Graph Transformer superiority,
GHD positional encoding, cheap steady supervision, full-cycle output,
hemodynamic-index derivation, or the broad observation that a small global
field score can coexist with worse derived-marker error.

The exact acquired processed-v4 snapshot is not silently equated with that
manuscript cohort. D4 observed 578 cases, while the paper says 808 and the
current public dataset page says 730 pulsatile cases. D5 groups exact/numerical
GHD copies and freezes 406/51/51 train/validation/outer components. This is a
reproducible synthetic-geometry split, not proof that the prior split leaked
and not a patient-, site- or generator-family split.

### Cross-vascular strong controls

[Rygiel et al., arXiv:2507.22817](https://arxiv.org/abs/2507.22817) already use
an E(3)-equivariant LaB-GATr to predict transient WSS in 100 CTA-derived
abdominal-aortic-aneurysm anatomies, evaluate an external cohort and study
boundary-condition, topology, remodelling and mesh-resolution shifts. They
derive TAWSS and OSI and explicitly report high-frequency directional
over-smoothing. Equivariance, robust geometric descriptors, external
generalisation and TAWSS/OSI evaluation are therefore strong controls rather
than novelty.

[Deep vectorised operators](https://doi.org/10.1016/j.cmpb.2025.108958)
already provide a vectorised transient-hemodynamics operator and a public
LaB-VaTr implementation. Their role is a reimplementable cross-vascular
baseline, not evidence that AneuG cycle-function fidelity is solved.

### Correction of an earlier citation error

Earlier 2026-08-13 AURORA notes incorrectly described
[NOEM](https://doi.org/10.1038/s43588-026-00974-2) as a generic hard-constraint
output transformation. The cited paper is actually a finite-element method
that embeds reusable neural-operator elements in selected subdomains. It does
not establish that claimed collision. Those historical records remain in git,
but their scientific characterization is superseded here.

The relevant generic collision is instead
[Adaptive Correction for Ensuring Conservation Laws in Neural Operators
(arXiv:2505.24579v2)](https://arxiv.org/abs/2505.24579), which applies a
learnable plug-and-play correction to enforce linear and quadratic conserved
quantities exactly. It is an arXiv/ICLR-2026-review-stage source, not treated as
peer-reviewed medical evidence, but it blocks novelty claims based only on an
exact differentiable output correction. TAWSS and OSI are not themselves
conservation laws, so the source does not occupy the aneurysm experiment; it
does make the proposed readout a minimal application mechanism rather than a
general neural-operator invention.

## Residual gap

The prior results expose, but do not isolate or repair, a useful conjunction:

1. **Metric ambiguity.** Maximum-normalized \(rL_2^*\) can look excellent while
   conventional field and OSI errors remain much larger. Reshaped SSIM does
   not respect mesh adjacency, and rendered SSIM depends on viewpoints.
2. **No matched attribution.** The prior compares different architectures and
   output families; it does not hold backbone, information, compute and vector
   field error fixed while changing only cycle-functional treatment.
3. **No consistency mechanism.** TAWSS/OSI/RRT are evaluated after field
   prediction, but the network is not required to represent the mean vector,
   mean magnitude and temporal residual coherently.
4. **No leakage-aware released-snapshot evidence.** The exact acquired 578-case
   object and D5 component-held-out split have not been evaluated.

RRT is not an independent third target. With
\(m=E_t[\tau_t]\), \(a=E_t[\|\tau_t\|]\),
\(\mathrm{OSI}=\tfrac12(1-\|m\|/a)\), the usual definition reduces to
\(\mathrm{RRT}=1/\|m\|\). AURORA will report denominator stability or
log-RRT on a prospectively supported subset, never count RRT as an additional
independent co-primary endpoint.

## Provisional mechanism, not yet a selected architecture

If D6 passes and a fresh matched baseline gate observes material functional
error, the smallest mechanism-linked comparison is:

- one shared GHD-aware GraphGPS/GINE geometry encoder and one shared periodic
  phase-query decoder;
- a direct tangent-vector cycle head as the primary baseline;
- the same head with soft TAWSS/mean-vector losses as the optimization control;
- a moment-consistent head that predicts tangent mean vector \(m\), mean
  magnitude \(a\geq\|m\|\), and a zero-mean tangent residual shape, then solves
  only the residual scale so the reconstructed cycle has exactly those
  predicted moments.

The head guarantees agreement between its transient output and its own
predicted TAWSS/OSI; it does not guarantee agreement with CFD. Any gain must
therefore come from more accurately learning \(m\), \(a\) and residual shape,
not from algebraically replacing the reference target. Tangent projection,
the Jensen cone and scalar root solve are controls. No method name is
warranted before evidence.

The separate [synthetic feasibility prototype](cycle-moment-projection-prototype-2026-08-16.md)
tests existence, Jensen-boundary ambiguity, rotation equivariance and finite
gradients without reading a real field or selecting this mechanism.

Graph U-Net and an official-code LaB-GATr or LaB-VaTr adaptation remain
external architecture controls where compute permits. The headline comparison
must use the same GHD-GraphGPS backbone so a head-level effect is attributable.

## Acceptance-oriented experiment ladder

1. **D6 train-only admission.** Check physical decoding, mesh/stored normals,
   tangency, temporal variation and moment support. Any outcome closes D6.
2. **Baseline reproduction on train/validation only.** Reproduce a credible
   direct GHD-GraphGPS baseline and record field, TAWSS and OSI errors. Do not
   expose the 51 outer components.
3. **Matched-failure gate.** Establish a material cycle-functional deficit at
   comparable validation field error. A low \(rL_2^*\) alone does not pass.
4. **Bounded mechanism development.** Compare direct, soft-loss and
   moment-consistent heads with identical encoder, information, optimizer,
   schedule and bounded compute. Select by a predeclared validation Pareto
   rule, not by outer performance.
5. **One-shot outer confirmation.** Evaluate frozen checkpoints and thresholds
   on 51 component-held-out geometries with paired component bootstrap
   intervals and seed-level consistency.

Primary reporting should use mesh-area-weighted physical vector error,
direction error above a train-defined magnitude mask, TAWSS error and OSI
absolute/calibrated error on prospectively supported nodes. Secondary reporting
may include low-TAWSS/high-OSI surface-burden error and log-RRT where its
denominator is identified. Every table reports the independent unit, seed
aggregation and paired uncertainty. Every qualitative panel uses the same
geometry, phase, coordinates, camera and reference-derived colour limits.

## Kill rules

The direction closes rather than being rhetorically repaired if:

- D6 fails or is execution-incomplete;
- a credible direct baseline cannot be reproduced on the exact snapshot;
- functional error vanishes after mesh-native, denominator-aware evaluation;
- the proposed gain appears only in \(rL_2^*\), rendered SSIM or RRT;
- a soft-loss control matches the moment-consistent head;
- endpoint improvement requires material vector-field degradation;
- effects reverse across seeds or are driven by a few components; or
- the paper needs patient, clinical-risk, rupture or waveform-generalisation
  language unsupported by this synthetic fixed-waveform dataset.

Until the preceding gates pass, the defensible label is **conditional
cycle-functional fidelity audit on a synthetic intracranial-aneurysm CFD
benchmark**, not a new neural operator or clinically validated surrogate.
