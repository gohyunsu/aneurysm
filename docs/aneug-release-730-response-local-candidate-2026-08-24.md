# Release-730 response/local candidate execution contract

## Decision

The 14,392-row processed steady asset is not omitted from the study. After
excluding all 407 exact-GHD overlaps with transient train, validation, locked
test and processed-only rows, the same ordered 13,985 eligible steady rows
must be exposed to the selected control and proposal. The final design is a
matched 2-by-2 comparison:

| Model factor | Transient only (T) | Identical eligible steady exposure (T+S) |
|---|---:|---:|
| strongest selected control | required | required |
| selected aligned candidate | required | required |

This separates the model effect, steady-information effect and their
interaction. It also prevents a proposal-only information advantage. The
published count of 14,000 steady simulations and the exact processed count of
14,392 rows remain distinct facts. Steady supervision is a fairness and
label-efficiency factor, not a novelty claim: Sheng et al. already report
mixed steady/transient training, a predicted steady-WSS prior and transient
label-efficiency experiments.

## Why a transient-only development runner is still necessary

The present runner executes only validation development cells. It first asks
whether the response/local decomposition and same-field functional objective
have any effect before the much more expensive matched T/T+S confirmation.
This does not justify excluding steady rows from the paper. It prevents the
steady-data effect from masking whether the candidate architecture itself
works.

The serial evidence order is:

1. train-only response oracle and rank nomination;
2. direct GHD--GPS and Transolver controls;
3. response-only and response-plus-residual field-only cells;
4. three objective-matched fine-tunes from the exact same combined
   field-only checkpoint;
5. selected control/proposal T/T+S factorial with the exact matched steady
   stream and exposure schedule;
6. fresh-seed confirmation, followed by one locked-test scope event.

The 73 locked-test cases and 79 processed-only rows are absent from every
runner input. They cannot be opened by setting a command-line flag.

## Executable model

One release-730 GHD-conditioned GINE/GPS mesh U-Net encodes coordinates,
derived normals, relative vertex area and the 432-D geometry descriptor. The
same node features feed both branches:

- their area-weighted pool predicts a positive full-cycle response amplitude
  and coordinates in the train-only response basis;
- the per-node features decode a phase-specific Cartesian residual;
- a nodewise, phase-shared sigmoid gate controls where that residual is used.

The response basis is a separately hash-bound oracle artifact. It follows the
model across devices but is excluded from model checkpoints, avoiding up to
about 3.18 GiB of duplicated fixed rank-256 data per checkpoint. No tangent,
periodic or basis-complement projection is imposed. Response-basis leakage is
a detached diagnostic, not a hidden regularizer. Its large basis projection is
skipped during training and intermediate validation and computed for the final
report; this changes neither a decoded field nor checkpoint selection.

For response-only training, the local cycle head and spatial gate are frozen.
For the combined cell they are active. The common single-field steady head is
frozen in every transient-only cell and becomes active only in the later
matched T+S runner. Active parameter count is reported separately from total
registered parameter count.

## Objective attribution

Architecture development uses the same area/phase-weighted physical vector
WSS relative squared error and the same 251/80/40 maximum/minimum/patience
schedule as GHD--GPS. It contains exactly two GPU cells:

- response only, field only;
- response plus local residual, field only.

Functional development contains exactly three cells. Every cell reloads the
same selected combined field-only checkpoint and receives the same 60/15/12
fine-tuning schedule:

- field only;
- field plus mean-vector, TAWSS and valid-support OSI terms, scalarized after
  initial-checkpoint train normalization;
- the same terms with field-anchored gradient conflict control.

The training normalizers use all and only the 584 training cases. Checkpoint
utility normalizers use the same initial checkpoint on all and only the 73
validation cases. No absolute threshold or automatic winner is defined.

## Evaluation and reviewer-facing interpretation

Every decoded output is evaluated in the raw released physical Cartesian WSS
space. The result reports case-level field relative L2, TAWSS normalized
absolute error, reference-support OSI MAE and its same-support area coverage,
mean-vector error, low-TAWSS error,
peak-systolic error, normal-component error, gate mean and basis leakage,
together with active parameters, peak GPU memory and elapsed time. Phases and
vertices are never treated as independent statistical samples.

The architecture is not independently novel merely because it combines a
response basis, residual branch or functional loss. Its paper role remains
conditional: under identical transient and steady information, it must
improve field, TAWSS and OSI fidelity over a strong direct control, and each
reported component must explain a distinct observed gain. If it does not, the
result is preserved as a failed candidate and the manuscript claim is not
made.

## Runtime and provenance

`src/aurora/aneug_release_730_response_local_candidate.py` implements the
runner. `cluster/pbs_aneug_release_730_response_local_candidate_v1.pbs`
executes one activation-bound cell on one introai9 A6000. It requires exact
oracle basis, oracle terminal, GHD--GPS terminal, Transolver terminal, split
and train-audit hashes before data loading. A genuine infrastructure
interruption may resume only from an exact checkpoint plus a preserved
noncomplete terminal record, into a new append-only run root. Completed
scientific runs are not continuation inputs.

This is execution readiness, not an activation, experiment result, rank
choice, paper performance claim or permission to use another server.
