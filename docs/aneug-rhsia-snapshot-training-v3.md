# Native RHSIA snapshot training and fair exposure accounting

`aneug_rhsia_snapshot_training.py` connects the genuine phase-conditioned model
to admitted geometry providers, the existing leakage-audited steady stream and
the same physical evaluation functions used by complete-cycle comparators.
Scientific configurations, data identifiers, generated results and execution
activations remain private. No training configuration is activated by this file.

## Source recipe versus explicit task adaptation

The pinned author `RegisteredMultiTaskImageDataset` enumerates each transient
geometry x each available phase. With our fixed development cohort, a complete
transient epoch contains 584 x 80 = 46,720 snapshots. Adding one pass through
the existing eligible steady pool gives 60,705 samples. It is not a 584-forward
cycle epoch and not a 584-snapshot epoch. The paper states dynamic steady/
transient sampling, while the released graph-encoder path explicitly asserts
that steady encoding is unimplemented. Therefore our admitted steady spectral
provider closes a missing release path; it is not an exact author trainer run.

The trainer supports real graph microbatches, including batch ten, with
concatenated node descriptors and offset mesh edges. No edge can cross graphs.
Smaller microbatches with accumulated gradients are separately labelled: they
do not reproduce batch-ten normalization, even when optimizer batch size is ten.
All source-sized model dimensions remain outside this trainer in the pinned
scientific model configuration; small test fixtures are never training recipes.

`phases_per_geometry == 80` retains full source-style enumeration. A smaller
value is a declared compute-budget adaptation that traverses shuffled phase
cycles, rather than selecting a permanent phase subset. Transient phase/order
choices are identical across paired T and T+S schedules. Steady examples are
interleaved from the existing deterministic eligible-pool schedule.

The objective is the common area/phase-weighted physical cycle-relative squared
error, NOT the author's channel-normalized MSE. Each transient snapshot uses
its entire reference cycle's energy as denominator. Averaging all phase losses
therefore equals the existing complete-cycle objective, including its gradient.
Normalizing each snapshot by its own energy would be a different objective.
Steady labels use the analogous single-field loss and a declared multiplier;
the mixed minibatch mean and T/S sample counts specify the regime weighting.

Steady samples enter through phase -1 and the existing post-bias temporal mask.
Their actual WSS is not identified with any transient phase or temporal mean.
An all-steady microbatch may legitimately have no temporal-encoder gradients;
disconnected parameters are checked over the mixed epoch. Only the requested
reference snapshot moves to GPU during training, not an unnecessary 80-phase
label tensor per forward. Learned geometry encodings are never cached across
training calls or optimizer updates.

## Evaluation, continuation and evidence

Validation uses all phases and the identical field/TAWSS/valid-support OSI
functions as the cycle trainer. Existing model eval reuses one geometry encoding
within each complete cycle but still performs every conditioned graph pass.
Earliest minimum validation field rL2 selects the checkpoint. Selection epochs,
parameter count, phase/steady exposures, graph encodings, actual model calls,
updates, validation calls, elapsed time and peak memory are separately recorded.
Timing here includes geometry assembly/data transfer; the independent GPU
measurement measures a narrower warmed inference path. Do not conflate them.

Epoch checkpoints preserve model buffers, optimizer, scheduler, RNG, selection,
coverage and history. A hash-bound continuation requires unchanged scientific
provenance and optimization except a larger terminal epoch, writes a fresh
output directory, and preserves parent evidence. A CPU dropout regression matches
uninterrupted and resumed weights/moments/RNG exactly. This does not promise
cross-hardware or nondeterministic-CUDA bit equality. Additional validation at a
previous segment's terminal epoch remains part of its actual selection history.

Twelve new synthetic tests include real PyG GINE/Performer mixed-snapshot
learning, real graph-batch support, exposure accounting, scope failures, physical
objective equivalence, full evaluator identity and continuation. Actual full-size
GPU cost and sufficient real-data learning curves remain required. Choose a
feasible, prospectively documented batch/sampling/validation budget from those
measurements; do not shrink the model or call one sampled phase a native epoch.

Primary references: [Sheng/RHSIA III-E--H](https://arxiv.org/html/2601.19876v2)
and the [pinned released dataset](https://github.com/WenHaoDing/AneuG-Flow/blob/4a090a0f12538deef6fcea88b81afe78ce38152e/new_version/datasets_wss_optimized.py).
