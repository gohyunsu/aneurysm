# Matched transient/steady training for release-730

## Reviewer-facing decision

The processed steady cohort must not be silently omitted, but it also must not
be given only to the proposal. The executable final-development question is a
selected model by information factorial:

| | Transient-only (T) | Eligible steady augmentation (T+S) |
|---|---:|---:|
| selected strongest control | required | required |
| selected proposal | required | required |

The processed archive contains 14,392 steady rows. The prior geometry-only
overlap audit excludes 407 exact-GHD matches to every transient partition and
processed-only extra, leaving one ordered 13,985-row cohort. Both T+S cells use
the same eligible indices, SHA-256-ranked no-replacement cycle and schedule
seed. The public source's rounded 14,000 count and the processed cardinality
must remain distinct in the manuscript.

This design does not claim that steady augmentation is novel. Sheng et al.
already use steady/transient mixing, a predicted steady-WSS prior and
label-efficiency analysis. The factorial is a fairness and information-budget
control. Primary method comparisons are proposal versus control within T and
within T+S. Within-model T-to-T+S differences and the interaction estimate the
registered augmentation protocol, including its additional compute; they are
not label-only causal effects.

### Bounded auxiliary-path attribution

Two single-seed development sidecars, control T+M and proposal T+M, make the
steady comparison less confounded. T+M reuses exactly the T+S single-field
head and coefficient and makes one second geometry forward/backward pass per
transient training case. Its target is the same case's 80-phase mean vector
WSS. Its output scale is the area-weighted RMS of exactly those 584 train-only
cycle-mean targets, and it reads no steady WSS row.

T+S-minus-T+M is narrower than T+S-minus-T: it helps determine whether an
observed benefit requires the eligible steady labels rather than merely an
auxiliary head and second model pass. It is still not a causal steady-label
effect because the targets, storage I/O and some system-level work differ.
Accordingly T+M neither replaces nor blocks the primary T/T+S factorial. It
is required only before making a steady-specific interpretation.

## Exact pairing and target

Each epoch contains all 584 transient training cases. In T+S, exactly 584
eligible steady rows are paired with them—one steady row per transient case.
Rows are visited without replacement until all 13,985 eligible rows have been
exposed, then a new deterministic SHA-256-ranked cycle begins. At the minimum
80 epochs this gives 46,720 steady exposures and 3–4 visits per row; at the
251-epoch ceiling it gives 146,584 exposures and 10–11 visits per row. Every
checkpoint and terminal result records the exact exposure count and prefix
digest.

Both models use a shared geometry encoder and a separate single-field steady
head. A steady WSS field is never repeated across 80 phases and receives no
phase or waveform token. The common head predicts a dimensionless field and
is converted to physical units with the eligible-steady vector RMS from the
separate descriptive scale audit. That scale is a numerical output
parameterization, not a loss weight.

The T+S loss adds one area-weighted, case-relative steady field squared error
to the dimensionless transient cycle objective with coefficient one. T+M adds
the corresponding cycle-mean field term with coefficient one, while T freezes
the registered head. All cells retain identical cycle initialization,
transient order, seed, optimizer and validation rule. T+M and T+S activate the
same head and one auxiliary model pass per transient case; their target and
output scale follow their distinct train-only information sources.

## Selected model space

The control is selected on validation from the exact release-730 GHD--GPS and
Transolver direct comparators. The proposal is selected from the response plus
nodewise local-residual model, its oracle-nominated rank and the three
predeclared objectives: field-only, complete scalarized alignment or complete
field-anchored alignment. Selection requires a private, validation-only record
binding all terminal development evidence. The record rejects locked-test or
79-extra use and defines no absolute threshold.

Every factorial cell starts from scratch with seed 1103 and the common
251/80/40 maximum/minimum/patience schedule. For an aligned proposal, the
field/mean-vector/TAWSS/OSI training normalizers use all and only the initial
584 training predictions. Checkpoint utility normalizers use the same initial
model on all and only the 73 validation cases. T and T+S therefore begin from
identical cycle weights and objective normalization.

## Executable boundary

`src/aurora/aneug_release_730_matched_training.py` implements the four primary
factorial cells and two T+M sidecars.
`cluster/pbs_aneug_release_730_matched_training_v1.pbs` executes exactly one
activation-bound cell on one introai9 A6000. Before data loading it requires:

- the exact clean Quality-passed public commit;
- a private all-terminal development evidence bundle;
- the validation-only selected-model record;
- the descriptive eligible-steady scale result;
- the split, train audit and private overlap evidence;
- the exact scope, exposure and model configs;
- the separately hash-bound train-only response basis for proposal cells.

Transient-only execution reads the steady archive only for the common
nine-channel physical decoder normalization already required by direct
comparators; it indexes no steady WSS row. Eligible-steady execution uses the
lazy reader and decodes only scheduled rows. Neither CLI nor PBS script has a
locked-test or processed-only-extra input.

A genuine noncomplete infrastructure interruption may resume only from a
fresh activation, the preserved nonzero-exit terminal record and an exact
state checkpoint. The checkpoint restores model, optimizer, scheduler,
patience, RNG and the recomputed steady exposure prefix. A completed
scientific run is not a continuation input.

## Output and interpretation

Each cell emits the schema already consumed by the matched-information
analyzer: 73 identifier-free case rows, field relative L2, mean-vector error,
TAWSS normalized absolute error, valid-support OSI MAE/coverage, training
steps, active parameters, GPU reservation time, memory and exact data
exposure. It creates no automatic winner, novelty conclusion, test authority
or paper claim.

The separate auxiliary-attribution analyzer accepts only the two T+M and two
T+S terminal cells, enforces matching model/protocol lineage within each role
and reports paired T+S-minus-T+M contrasts. It explicitly records that this is
not fully compute-matched, not a causal steady-label effect and not an
automatic method-selection gate.

This code is readiness only. It cannot run until the oracle, direct controls,
candidate ablations, scale audit and selection record all exist and a fresh
private activation binds them.
